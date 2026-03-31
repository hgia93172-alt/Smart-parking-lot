from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from django_main.R import R

F = TypeVar("F", bound=Callable[..., Any])


def _get_request_from_args(args: tuple[Any, ...], kwargs: dict[str, Any]):
    req = kwargs.get("request")
    if req is not None:
        return req
    if len(args) >= 2 and hasattr(args[1], "user"):
        return args[1]
    if len(args) >= 1 and hasattr(args[0], "user"):
        return args[0]
    return None


def login_required(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        request = _get_request_from_args(args, kwargs)
        if request is None or not getattr(request.user, "is_authenticated", False):
            return R.unauthorized(msg="请先登录")
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def admin_required(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        request = _get_request_from_args(args, kwargs)
        if request is None or not getattr(request.user, "is_authenticated", False):
            return R.unauthorized(msg="请先登录")
        user = request.user
        if not (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
            return R.forbidden(msg="需要管理员权限")
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]

