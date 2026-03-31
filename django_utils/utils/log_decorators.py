from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from django.http import HttpRequest

from django_utils.models import OperationLog

F = TypeVar("F", bound=Callable[..., Any])


def _get_request_from_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> HttpRequest | None:
    """从视图方法/函数的入参中尽可能提取 request。"""
    req = kwargs.get("request")
    if req is not None:
        return req
    if len(args) >= 2 and hasattr(args[1], "META"):
        return args[1]
    if len(args) >= 1 and hasattr(args[0], "META"):
        return args[0]
    return None


def _get_client_ip(request: HttpRequest) -> str | None:
    """尽可能获取客户端 IP（优先 X-Forwarded-For）。"""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if isinstance(xff, str) and xff.strip():
        return xff.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR")


def _extract_business_code(resp: Any) -> int | None:
    """从统一返回结构中提取业务 code。"""
    data = getattr(resp, "data", None)
    if isinstance(data, dict):
        code = data.get("code")
        return int(code) if isinstance(code, int) else None
    return None


def log_operation(action: str = "", remark: str = "") -> Callable[[F], F]:
    """记录操作日志的装饰器：用于 DRF/Django 视图函数或视图方法。"""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            request = _get_request_from_args(args, kwargs)
            resp: Any = None
            err: Exception | None = None
            try:
                resp = func(*args, **kwargs)
                return resp
            except Exception as e:
                err = e
                raise
            finally:
                if request is None:
                    return

                status_code = getattr(resp, "status_code", None)
                response_code = _extract_business_code(resp)
                is_success = True
                if isinstance(status_code, int) and status_code >= 400:
                    is_success = False
                if response_code is not None and response_code != 20001:
                    is_success = False

                user = getattr(request, "user", None)
                operator = user if getattr(user, "is_authenticated", False) else None
                detail = str(err) if err is not None else ""

                OperationLog.objects.create(
                    operator=operator,
                    action=action or "",
                    remark=remark or "",
                    path=str(getattr(request, "path", "")) or "",
                    method=str(getattr(request, "method", "")) or "",
                    ip=_get_client_ip(request),
                    status_code=int(status_code) if isinstance(status_code, int) else None,
                    response_code=response_code,
                    success=is_success,
                    detail=detail,
                )

        return wrapper  # type: ignore[return-value]

    return decorator
