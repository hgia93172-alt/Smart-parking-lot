from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.authtoken.models import Token

from django_auth.models import UserProfile
from django_auth.serializers import (
    LoginSerializer,
    MeUpdateSerializer,
    RegisterSerializer,
    UserAdminCreateSerializer,
    UserAdminListSerializer,
    UserAdminUpdateSerializer,
)
from django_auth.utils.decorators import admin_required, login_required
from django_main.R import R
from django_utils.utils.log_decorators import log_operation

User = get_user_model()


def _get_or_create_profile(user) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def _user_data(user):
    profile = getattr(user, "profile", None) or _get_or_create_profile(user)
    return {
        "id": user.id,
        "username": user.username,
        "role": profile.role,
        "is_active": bool(getattr(user, "is_active", True)),
        "is_staff": bool(getattr(user, "is_staff", False)),
        "is_superuser": bool(getattr(user, "is_superuser", False)),
        "is_admin": bool(user.is_staff or user.is_superuser),
        "date_joined": getattr(user, "date_joined", None),
    }


def _pagination_params(request: Request) -> tuple[bool, int, int]:
    """解析分页参数：若传入 page/page_size 则启用分页。"""
    qp = getattr(request, "query_params", {}) or {}
    enabled = "page" in qp or "page_size" in qp
    if not enabled:
        return False, 1, 20
    try:
        page = int(qp.get("page", 1) or 1)
    except Exception:
        page = 1
    try:
        page_size = int(qp.get("page_size", 20) or 20)
    except Exception:
        page_size = 20
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100
    return True, page, page_size


def _paged_response(items, *, page: int, page_size: int, total: int):
    """构造分页返回结构。"""
    return {"count": total, "page": page, "page_size": page_size, "results": items}


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    @log_operation(action="auth_register", remark="注册")
    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        data = _user_data(user)
        data["token"] = token.key
        return R.ok(data=data, msg="注册成功")


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    @log_operation(action="auth_login", remark="登录")
    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        user = serializer.validated_data["user"]
        _get_or_create_profile(user)
        token, _ = Token.objects.get_or_create(user=user)
        data = _user_data(user)
        data["token"] = token.key
        return R.ok(data=data, msg="登录成功")


class LogoutView(GenericAPIView):
    @log_operation(action="auth_logout", remark="退出登录")
    @login_required
    def post(self, request: Request):
        Token.objects.filter(user=request.user).delete()
        return R.ok(msg="退出成功")


class MeUpdateView(GenericAPIView):
    serializer_class = MeUpdateSerializer

    @log_operation(action="me_get", remark="获取当前用户信息")
    @login_required
    def get(self, request: Request):
        return R.ok(data=_user_data(request.user))

    @log_operation(action="me_update", remark="更新当前用户信息")
    @login_required
    def put(self, request: Request):
        return self._update(request, partial=False)

    @log_operation(action="me_update", remark="更新当前用户信息")
    @login_required
    def patch(self, request: Request):
        return self._update(request, partial=True)

    def _update(self, request: Request, partial: bool):
        serializer = self.get_serializer(
            instance=request.user,
            data=request.data,
            partial=partial,
            context={"user": request.user},
        )
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        user = serializer.save()
        return R.ok(data=_user_data(user), msg="修改成功")


class AdminUserListView(GenericAPIView):
    serializer_class = UserAdminCreateSerializer

    @log_operation(action="admin_user_list", remark="管理员查询用户列表")
    @admin_required
    def get(self, request: Request):
        enabled, page, page_size = _pagination_params(request)
        qs = User.objects.all().select_related("profile").order_by("id")
        if not enabled:
            serializer = UserAdminListSerializer(qs, many=True)
            return R.ok(data=serializer.data)
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = UserAdminListSerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))

    @log_operation(action="admin_user_create", remark="管理员创建用户")
    @admin_required
    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        user = serializer.save()
        return R.ok(data=_user_data(user), msg="创建成功")


class AdminUserDetailView(GenericAPIView):
    serializer_class = UserAdminUpdateSerializer

    @log_operation(action="admin_user_detail", remark="管理员查看用户详情")
    @admin_required
    def get(self, request: Request, user_id: int):
        user = User.objects.filter(pk=user_id).select_related("profile").first()
        if user is None:
            return R.fail(msg="用户不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return R.ok(data=_user_data(user))

    @log_operation(action="admin_user_update", remark="管理员更新用户")
    @admin_required
    def put(self, request: Request, user_id: int):
        return self._update(request, user_id=user_id, partial=False)

    @log_operation(action="admin_user_update", remark="管理员更新用户")
    @admin_required
    def patch(self, request: Request, user_id: int):
        return self._update(request, user_id=user_id, partial=True)

    @log_operation(action="admin_user_delete", remark="管理员删除用户")
    @admin_required
    def delete(self, request: Request, user_id: int):
        user = User.objects.filter(pk=user_id).first()
        if user is None:
            return R.fail(msg="用户不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return R.ok(msg="删除成功")

    def _update(self, request: Request, user_id: int, partial: bool):
        """管理员更新指定用户。"""
        user = User.objects.filter(pk=user_id).select_related("profile").first()
        if user is None:
            return R.fail(msg="用户不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(
            instance=user,
            data=request.data,
            partial=partial,
            context={"user": user},
        )
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        serializer.save()
        return R.ok(data=_user_data(user), msg="修改成功")
