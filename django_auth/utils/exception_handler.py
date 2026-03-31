from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework.views import exception_handler as drf_exception_handler

from django_main.R import R


def custom_exception_handler(exc, context):
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return R.unauthorized(msg=str(getattr(exc, "detail", "请先登录")))
    if isinstance(exc, PermissionDenied):
        return R.forbidden(msg=str(getattr(exc, "detail", "需要管理员权限")))

    response = drf_exception_handler(exc, context)
    if response is None:
        return response
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return R.unauthorized(msg=str(response.data.get("detail", "请先登录")))
    if response.status_code == status.HTTP_403_FORBIDDEN:
        return R.forbidden(msg=str(response.data.get("detail", "需要管理员权限")))
    return response

