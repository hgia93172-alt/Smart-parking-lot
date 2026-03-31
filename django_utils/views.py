from __future__ import annotations

import mimetypes

from django.db.models import Count, F, Q
from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request

from django_auth.utils.decorators import admin_required, login_required
from django_main.R import R
from django_utils.models import (
    Article,
    ArticleCategory,
    ArticleComment,
    ArticleFavorite,
    ArticleLike,
    OperationLog,
    UserFile,
)
from django_utils.serializers import (
    ArticleAdminCreateUpdateSerializer,
    ArticleAdminSerializer,
    ArticleCategorySerializer,
    ArticleCommentCreateSerializer,
    ArticleCommentSerializer,
    ArticlePublicDetailSerializer,
    ArticlePublicListSerializer,
    FileUploadSerializer,
    OperationLogSerializer,
    UserFileSerializer,
    UserFileUpdateSerializer,
)
from django_utils.utils.log_decorators import log_operation


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


def _can_access_file(request: Request, user_file: UserFile) -> bool:
    """判断当前请求用户是否可访问目标文件。"""
    user = request.user
    return bool(
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or (user_file.uploader_id is not None and user_file.uploader_id == user.id)
    )


class FileUploadView(GenericAPIView):
    serializer_class = FileUploadSerializer

    @log_operation(action="file_upload", remark="上传文件")
    @login_required
    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        user_file = serializer.save()
        return R.ok(data=UserFileSerializer(user_file).data, msg="上传成功")


class FileListView(GenericAPIView):
    @log_operation(action="file_list", remark="查询文件列表")
    @login_required
    def get(self, request: Request):
        enabled, page, page_size = _pagination_params(request)
        qs = UserFile.objects.filter(uploader=request.user).order_by("-id")
        if not enabled:
            return R.ok(data=UserFileSerializer(qs, many=True).data)
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = UserFileSerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))


class FileDownloadView(GenericAPIView):
    @log_operation(action="file_download", remark="下载文件")
    @login_required
    def get(self, request: Request, file_id: int):
        user_file = UserFile.objects.filter(pk=file_id).select_related("uploader").first()
        if user_file is None:
            return R.fail(msg="文件不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)

        if not _can_access_file(request, user_file):
            return R.forbidden(msg="无权限访问该文件")

        file_field = user_file.file
        if not file_field or not file_field.name:
            return R.fail(msg="文件不存在", code=40402, http_status=status.HTTP_404_NOT_FOUND)

        content_type, _ = mimetypes.guess_type(user_file.original_name)
        response = FileResponse(
            file_field.open("rb"),
            as_attachment=True,
            filename=user_file.original_name,
            content_type=content_type or "application/octet-stream",
        )
        return response


class FileDetailView(GenericAPIView):
    serializer_class = UserFileUpdateSerializer

    @log_operation(action="file_detail", remark="查看文件详情")
    @login_required
    def get(self, request: Request, file_id: int):
        user_file = UserFile.objects.filter(pk=file_id).select_related("uploader").first()
        if user_file is None:
            return R.fail(msg="文件不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        if not _can_access_file(request, user_file):
            return R.forbidden(msg="无权限访问该文件")
        return R.ok(data=UserFileSerializer(user_file).data)

    @log_operation(action="file_update", remark="修改文件信息")
    @login_required
    def put(self, request: Request, file_id: int):
        return self._update(request, file_id=file_id, partial=False)

    @log_operation(action="file_update", remark="修改文件信息")
    @login_required
    def patch(self, request: Request, file_id: int):
        return self._update(request, file_id=file_id, partial=True)

    @log_operation(action="file_delete", remark="删除文件")
    @login_required
    def delete(self, request: Request, file_id: int):
        user_file = UserFile.objects.filter(pk=file_id).select_related("uploader").first()
        if user_file is None:
            return R.fail(msg="文件不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)

        if not _can_access_file(request, user_file):
            return R.forbidden(msg="无权限删除该文件")

        file_field = user_file.file
        user_file.delete()
        if file_field:
            file_field.delete(save=False)
        return R.ok(msg="删除成功")

    def _update(self, request: Request, file_id: int, partial: bool):
        """更新文件元信息（目前支持修改 original_name）。"""
        user_file = UserFile.objects.filter(pk=file_id).select_related("uploader").first()
        if user_file is None:
            return R.fail(msg="文件不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        if not _can_access_file(request, user_file):
            return R.forbidden(msg="无权限修改该文件")
        serializer = self.get_serializer(instance=user_file, data=request.data, partial=partial)
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        updated = serializer.save()
        return R.ok(data=UserFileSerializer(updated).data, msg="修改成功")


class AdminFileListView(GenericAPIView):
    @log_operation(action="admin_file_list", remark="管理员查询文件列表")
    @admin_required
    def get(self, request: Request):
        enabled, page, page_size = _pagination_params(request)
        qs = UserFile.objects.all().order_by("-id")
        if not enabled:
            return R.ok(data=UserFileSerializer(qs, many=True).data)
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = UserFileSerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))


class AdminFileDeleteView(GenericAPIView):
    @admin_required
    @log_operation(action="admin_file_delete", remark="管理员删除文件")
    def delete(self, request: Request, file_id: int):
        user_file = UserFile.objects.filter(pk=file_id).first()
        if user_file is None:
            return R.fail(msg="文件不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)

        file_field = user_file.file
        user_file.delete()
        if file_field:
            file_field.delete(save=False)
        return R.ok(msg="删除成功")


class AdminLogListView(GenericAPIView):
    @log_operation(action="admin_log_list", remark="管理员查询日志列表")
    @admin_required
    def get(self, request: Request):
        enabled, page, page_size = _pagination_params(request)
        if not enabled:
            page, page_size = 1, 20
        qs = OperationLog.objects.all().select_related("operator").order_by("-id")
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = OperationLogSerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))


class AdminLogDeleteView(GenericAPIView):
    @admin_required
    @log_operation(action="admin_log_delete", remark="管理员删除日志")
    def delete(self, request: Request, log_id: int):
        log = OperationLog.objects.filter(pk=log_id).first()
        if log is None:
            return R.fail(msg="日志不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        log.delete()
        return R.ok(msg="删除成功")


class AdminLogClearView(GenericAPIView):
    @admin_required
    @log_operation(action="admin_log_clear", remark="管理员清空日志")
    def delete(self, request: Request):
        """清空所有操作日志（会保留本次清空操作产生的新日志记录）。"""
        deleted, _ = OperationLog.objects.all().delete()
        return R.ok(data={"deleted": int(deleted)}, msg="清空成功")


class AdminCategoryListView(GenericAPIView):
    serializer_class = ArticleCategorySerializer

    @log_operation(action="admin_category_list", remark="管理员查询文章分类列表")
    @admin_required
    def get(self, request: Request):
        enabled, page, page_size = _pagination_params(request)
        qs = ArticleCategory.objects.all().order_by("sort_order", "-id")
        keyword = (request.query_params.get("keyword") or "").strip()
        if keyword:
            qs = qs.filter(name__icontains=keyword)

        if not enabled:
            return R.ok(data=self.get_serializer(qs, many=True).data)

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = self.get_serializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))

    @log_operation(action="admin_category_create", remark="管理员创建文章分类")
    @admin_required
    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        cat = serializer.save()
        return R.ok(data=self.get_serializer(cat).data, msg="创建成功")


class AdminCategoryDetailView(GenericAPIView):
    serializer_class = ArticleCategorySerializer

    @log_operation(action="admin_category_detail", remark="管理员查看文章分类详情")
    @admin_required
    def get(self, request: Request, category_id: int):
        cat = ArticleCategory.objects.filter(pk=category_id).first()
        if cat is None:
            return R.fail(msg="分类不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return R.ok(data=self.get_serializer(cat).data)

    @log_operation(action="admin_category_update", remark="管理员更新文章分类")
    @admin_required
    def put(self, request: Request, category_id: int):
        return self._update(request, category_id=category_id, partial=False)

    @log_operation(action="admin_category_update", remark="管理员更新文章分类")
    @admin_required
    def patch(self, request: Request, category_id: int):
        return self._update(request, category_id=category_id, partial=True)

    @log_operation(action="admin_category_delete", remark="管理员删除文章分类")
    @admin_required
    def delete(self, request: Request, category_id: int):
        cat = ArticleCategory.objects.filter(pk=category_id).first()
        if cat is None:
            return R.fail(msg="分类不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        cat.delete()
        return R.ok(msg="删除成功")

    def _update(self, request: Request, category_id: int, partial: bool):
        """更新文章分类。"""
        cat = ArticleCategory.objects.filter(pk=category_id).first()
        if cat is None:
            return R.fail(msg="分类不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance=cat, data=request.data, partial=partial)
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        updated = serializer.save()
        return R.ok(data=self.get_serializer(updated).data, msg="修改成功")


def _article_qs_with_counts(qs):
    """为文章 QuerySet 补齐点赞/收藏/评论数量。"""
    return qs.annotate(
        like_count=Count("likes", distinct=True),
        favorite_count=Count("favorites", distinct=True),
        comment_count=Count("comments", filter=Q(comments__is_deleted=False), distinct=True),
    )


class AdminArticleListView(GenericAPIView):
    serializer_class = ArticleAdminCreateUpdateSerializer

    @log_operation(action="admin_article_list", remark="管理员查询文章列表")
    @admin_required
    def get(self, request: Request):
        enabled, page, page_size = _pagination_params(request)
        qs = Article.objects.all().select_related("category", "author").order_by("-id")
        keyword = (request.query_params.get("keyword") or "").strip()
        if keyword:
            qs = qs.filter(title__icontains=keyword)
        category_id = request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)
        status_val = (request.query_params.get("status") or "").strip()
        if status_val:
            qs = qs.filter(status=status_val)
        qs = _article_qs_with_counts(qs)

        if not enabled:
            return R.ok(data=ArticleAdminSerializer(qs, many=True).data)

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = ArticleAdminSerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))

    @log_operation(action="admin_article_create", remark="管理员创建文章")
    @admin_required
    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        article: Article = serializer.save()
        if article.status == Article.STATUS_PUBLISHED and article.published_at is None:
            article.published_at = timezone.now()
            article.save(update_fields=["published_at"])
        if article.status != Article.STATUS_PUBLISHED and article.published_at is not None:
            article.published_at = None
            article.save(update_fields=["published_at"])
        article = _article_qs_with_counts(Article.objects.filter(pk=article.id).select_related("category", "author")).first()
        return R.ok(data=ArticleAdminSerializer(article).data if article else None, msg="创建成功")


class AdminArticleDetailView(GenericAPIView):
    serializer_class = ArticleAdminCreateUpdateSerializer

    @log_operation(action="admin_article_detail", remark="管理员查看文章详情")
    @admin_required
    def get(self, request: Request, article_id: int):
        article = (
            _article_qs_with_counts(Article.objects.filter(pk=article_id).select_related("category", "author"))
            .first()
        )
        if article is None:
            return R.fail(msg="文章不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return R.ok(data=ArticleAdminSerializer(article).data)

    @log_operation(action="admin_article_update", remark="管理员更新文章")
    @admin_required
    def put(self, request: Request, article_id: int):
        return self._update(request, article_id=article_id, partial=False)

    @log_operation(action="admin_article_update", remark="管理员更新文章")
    @admin_required
    def patch(self, request: Request, article_id: int):
        return self._update(request, article_id=article_id, partial=True)

    @log_operation(action="admin_article_delete", remark="管理员删除文章")
    @admin_required
    def delete(self, request: Request, article_id: int):
        article = Article.objects.filter(pk=article_id).first()
        if article is None:
            return R.fail(msg="文章不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        cover = article.cover
        article.delete()
        if cover:
            cover.delete(save=False)
        return R.ok(msg="删除成功")

    def _update(self, request: Request, article_id: int, partial: bool):
        """更新文章。"""
        article = Article.objects.filter(pk=article_id).first()
        if article is None:
            return R.fail(msg="文章不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance=article, data=request.data, partial=partial, context={"request": request})
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        updated: Article = serializer.save()
        if updated.status == Article.STATUS_PUBLISHED and updated.published_at is None:
            updated.published_at = timezone.now()
            updated.save(update_fields=["published_at"])
        if updated.status != Article.STATUS_PUBLISHED and updated.published_at is not None:
            updated.published_at = None
            updated.save(update_fields=["published_at"])
        updated = (
            _article_qs_with_counts(Article.objects.filter(pk=updated.id).select_related("category", "author"))
            .first()
        )
        return R.ok(data=ArticleAdminSerializer(updated).data if updated else None, msg="修改成功")


class ArticlePublicListView(GenericAPIView):
    @log_operation(action="article_public_list", remark="用户查询文章列表")
    @login_required
    def get(self, request: Request):
        enabled, page, page_size = _pagination_params(request)
        qs = (
            Article.objects.filter(status=Article.STATUS_PUBLISHED)
            .select_related("category")
            .order_by("-published_at", "-id")
        )
        keyword = (request.query_params.get("keyword") or "").strip()
        if keyword:
            qs = qs.filter(title__icontains=keyword)
        category_id = request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)
        qs = _article_qs_with_counts(qs)

        if not enabled:
            return R.ok(data=ArticlePublicListSerializer(qs, many=True).data)

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = ArticlePublicListSerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))


class ArticlePublicCategoryListView(GenericAPIView):
    @log_operation(action="article_public_category_list", remark="用户查询文章分类列表")
    @login_required
    def get(self, request: Request):
        """返回用户端可用的文章分类列表（仅启用的分类）。"""
        enabled, page, page_size = _pagination_params(request)
        qs = ArticleCategory.objects.filter(is_active=True).order_by("sort_order", "-id")
        if not enabled:
            return R.ok(data=ArticleCategorySerializer(qs, many=True).data)
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = ArticleCategorySerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))


class ArticlePublicDetailView(GenericAPIView):
    @log_operation(action="article_public_detail", remark="用户查看文章详情")
    @login_required
    def get(self, request: Request, article_id: int):
        Article.objects.filter(pk=article_id, status=Article.STATUS_PUBLISHED).update(view_count=F("view_count") + 1)
        article = (
            _article_qs_with_counts(
                Article.objects.filter(pk=article_id, status=Article.STATUS_PUBLISHED).select_related("category")
            )
            .first()
        )
        if article is None:
            return R.fail(msg="文章不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return R.ok(data=ArticlePublicDetailSerializer(article, context={"request": request}).data)


class ArticleCommentListView(GenericAPIView):
    serializer_class = ArticleCommentCreateSerializer

    @log_operation(action="article_comment_list", remark="用户查询文章评论列表")
    @login_required
    def get(self, request: Request, article_id: int):
        enabled, page, page_size = _pagination_params(request)
        exists = Article.objects.filter(pk=article_id, status=Article.STATUS_PUBLISHED).exists()
        if not exists:
            return R.fail(msg="文章不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)

        qs = (
            ArticleComment.objects.filter(article_id=article_id, is_deleted=False)
            .select_related("user")
            .order_by("-id")
        )
        if not enabled:
            return R.ok(data=ArticleCommentSerializer(qs, many=True).data)

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = ArticleCommentSerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))

    @log_operation(action="article_comment_create", remark="用户发表评论")
    @login_required
    def post(self, request: Request, article_id: int):
        article = Article.objects.filter(pk=article_id, status=Article.STATUS_PUBLISHED).first()
        if article is None:
            return R.fail(msg="文章不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data, context={"request": request, "article": article})
        if not serializer.is_valid():
            return R.validation_error(msg="参数错误", data=serializer.errors)
        comment: ArticleComment = serializer.save()
        return R.ok(data=ArticleCommentSerializer(comment).data, msg="评论成功")


class ArticleLikeToggleView(GenericAPIView):
    @log_operation(action="article_like_toggle", remark="用户点赞/取消点赞")
    @login_required
    def post(self, request: Request, article_id: int):
        article = Article.objects.filter(pk=article_id, status=Article.STATUS_PUBLISHED).first()
        if article is None:
            return R.fail(msg="文章不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        obj = ArticleLike.objects.filter(article=article, user=request.user).first()
        liked = False
        if obj is None:
            ArticleLike.objects.create(article=article, user=request.user)
            liked = True
        else:
            obj.delete()
            liked = False
        like_count = ArticleLike.objects.filter(article=article).count()
        return R.ok(data={"liked": liked, "like_count": int(like_count)}, msg="操作成功")


class ArticleFavoriteToggleView(GenericAPIView):
    @log_operation(action="article_favorite_toggle", remark="用户收藏/取消收藏")
    @login_required
    def post(self, request: Request, article_id: int):
        article = Article.objects.filter(pk=article_id, status=Article.STATUS_PUBLISHED).first()
        if article is None:
            return R.fail(msg="文章不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        obj = ArticleFavorite.objects.filter(article=article, user=request.user).first()
        favorited = False
        if obj is None:
            ArticleFavorite.objects.create(article=article, user=request.user)
            favorited = True
        else:
            obj.delete()
            favorited = False
        favorite_count = ArticleFavorite.objects.filter(article=article).count()
        return R.ok(data={"favorited": favorited, "favorite_count": int(favorite_count)}, msg="操作成功")


class MeFavoriteArticlesView(GenericAPIView):
    @log_operation(action="me_favorite_articles", remark="用户查看我的收藏文章列表")
    @login_required
    def get(self, request: Request):
        enabled, page, page_size = _pagination_params(request)
        qs = (
            Article.objects.filter(
                favorites__user=request.user,
                status=Article.STATUS_PUBLISHED,
            )
            .select_related("category")
            .order_by("-favorites__created_at", "-id")
        )
        qs = _article_qs_with_counts(qs)

        if not enabled:
            return R.ok(data=ArticlePublicListSerializer(qs, many=True).data)

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = ArticlePublicListSerializer(qs[start:end], many=True).data
        return R.ok(data=_paged_response(items, page=page, page_size=page_size, total=total))
