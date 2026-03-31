from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response


class R:
    @staticmethod
    def ok(data: Any = None, msg: str = "OK", code: int = 20001) -> Response:
        return Response({"code": code, "msg": msg, "data": data}, status=status.HTTP_200_OK)

    @staticmethod
    def fail(
        msg: str = "FAIL",
        code: int = 40001,
        data: Any = None,
        http_status: int = status.HTTP_400_BAD_REQUEST,
    ) -> Response:
        return Response({"code": code, "msg": msg, "data": data}, status=http_status)

    @staticmethod
    def unauthorized(msg: str = "UNAUTHORIZED", code: int = 40101, data: Any = None) -> Response:
        return R.fail(msg=msg, code=code, data=data, http_status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def forbidden(msg: str = "FORBIDDEN", code: int = 40301, data: Any = None) -> Response:
        return R.fail(msg=msg, code=code, data=data, http_status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def validation_error(msg: str = "VALIDATION_ERROR", code: int = 40001, data: Any = None) -> Response:
        return R.fail(msg=msg, code=code, data=data, http_status=status.HTTP_400_BAD_REQUEST)

