from __future__ import annotations

from rest_framework import serializers

from django_utils.models import (
    Article,
    ArticleCategory,
    ArticleComment,
    ArticleFavorite,
    ArticleLike,
    OperationLog,
    UserFile,
)


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        """保存上传文件记录。"""
        request = self.context["request"]
        f = validated_data["file"]
        user_file = UserFile.objects.create(
            uploader=request.user if getattr(request.user, "is_authenticated", False) else None,
            file=f,
            original_name=getattr(f, "name", ""),
            size=getattr(f, "size", 0) or 0,
            content_type=getattr(f, "content_type", "") or "",
        )
        return user_file


class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ["id", "original_name", "size", "content_type", "created_at"]


class UserFileUpdateSerializer(serializers.Serializer):
    original_name = serializers.CharField(max_length=255, required=False)

    def update(self, instance: UserFile, validated_data):
        """更新用户文件元数据（不修改文件内容）。"""
        if "original_name" in validated_data:
            instance.original_name = validated_data["original_name"]
        instance.save(update_fields=["original_name"])
        return instance


class OperationLogSerializer(serializers.ModelSerializer):
    operator_username = serializers.SerializerMethodField()

    class Meta:
        model = OperationLog
        fields = [
            "id",
            "operator_username",
            "action",
            "remark",
            "path",
            "method",
            "ip",
            "status_code",
            "response_code",
            "success",
            "detail",
            "created_at",
        ]

    def get_operator_username(self, obj) -> str | None:
        """返回操作用户名（若为空则返回 None）。"""
        operator = getattr(obj, "operator", None)
        return getattr(operator, "username", None) if operator else None


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = [
            "id",
            "name",
            "description",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ArticleAdminSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    favorite_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "summary",
            "content",
            "status",
            "published_at",
            "view_count",
            "author_id",
            "category_id",
            "category_name",
            "cover_url",
            "like_count",
            "favorite_count",
            "comment_count",
            "created_at",
            "updated_at",
        ]

    def get_category_name(self, obj) -> str | None:
        """返回分类名称。"""
        cat = getattr(obj, "category", None)
        return getattr(cat, "name", None) if cat else None

    def get_cover_url(self, obj) -> str:
        """返回封面 URL（可能为空）。"""
        cover = getattr(obj, "cover", None)
        if cover and getattr(cover, "name", ""):
            try:
                return str(cover.url)
            except Exception:
                return ""
        return ""


class ArticleAdminCreateUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    summary = serializers.CharField(max_length=500, required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Article.STATUS_CHOICES, required=False)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    cover = serializers.FileField(required=False, allow_null=True)
    remove_cover = serializers.BooleanField(required=False)

    def create(self, validated_data):
        """创建文章。"""
        request = self.context["request"]
        category_id = validated_data.pop("category_id", None)
        category = None
        if category_id is not None:
            category = ArticleCategory.objects.filter(pk=category_id).first()
        article = Article.objects.create(
            author=request.user if getattr(request.user, "is_authenticated", False) else None,
            category=category,
            title=validated_data.get("title", ""),
            summary=validated_data.get("summary", "") or "",
            content=validated_data.get("content", "") or "",
            status=validated_data.get("status", Article.STATUS_DRAFT),
            cover=validated_data.get("cover"),
        )
        return article

    def update(self, instance: Article, validated_data):
        """更新文章。"""
        if "title" in validated_data:
            instance.title = validated_data["title"]
        if "summary" in validated_data:
            instance.summary = validated_data["summary"] or ""
        if "content" in validated_data:
            instance.content = validated_data["content"] or ""
        if "status" in validated_data:
            instance.status = validated_data["status"]
        if "category_id" in validated_data:
            category_id = validated_data.get("category_id")
            instance.category = ArticleCategory.objects.filter(pk=category_id).first() if category_id else None
        if validated_data.get("remove_cover") and "cover" not in validated_data:
            old_cover = instance.cover
            instance.cover = None
            if old_cover:
                old_cover.delete(save=False)
        if "cover" in validated_data:
            instance.cover = validated_data.get("cover")
        instance.save()
        return instance


class ArticlePublicListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    favorite_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "summary",
            "category_id",
            "category_name",
            "cover_url",
            "published_at",
            "view_count",
            "like_count",
            "favorite_count",
            "comment_count",
            "created_at",
            "updated_at",
        ]

    def get_category_name(self, obj) -> str | None:
        """返回分类名称。"""
        cat = getattr(obj, "category", None)
        return getattr(cat, "name", None) if cat else None

    def get_cover_url(self, obj) -> str:
        """返回封面 URL（可能为空）。"""
        cover = getattr(obj, "cover", None)
        if cover and getattr(cover, "name", ""):
            try:
                return str(cover.url)
            except Exception:
                return ""
        return ""


class ArticlePublicDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    favorite_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    liked = serializers.SerializerMethodField()
    favorited = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "summary",
            "content",
            "category_id",
            "category_name",
            "cover_url",
            "published_at",
            "view_count",
            "like_count",
            "favorite_count",
            "comment_count",
            "liked",
            "favorited",
            "created_at",
            "updated_at",
        ]

    def get_category_name(self, obj) -> str | None:
        """返回分类名称。"""
        cat = getattr(obj, "category", None)
        return getattr(cat, "name", None) if cat else None

    def get_cover_url(self, obj) -> str:
        """返回封面 URL（可能为空）。"""
        cover = getattr(obj, "cover", None)
        if cover and getattr(cover, "name", ""):
            try:
                return str(cover.url)
            except Exception:
                return ""
        return ""

    def get_liked(self, obj) -> bool:
        """返回当前用户是否点赞。"""
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if not getattr(user, "is_authenticated", False):
            return False
        return ArticleLike.objects.filter(article=obj, user=user).exists()

    def get_favorited(self, obj) -> bool:
        """返回当前用户是否收藏。"""
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None
        if not getattr(user, "is_authenticated", False):
            return False
        return ArticleFavorite.objects.filter(article=obj, user=user).exists()


class ArticleCommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = ArticleComment
        fields = [
            "id",
            "article_id",
            "user_id",
            "username",
            "parent_id",
            "content",
            "created_at",
            "updated_at",
        ]

    def get_username(self, obj) -> str | None:
        """返回评论用户名。"""
        u = getattr(obj, "user", None)
        return getattr(u, "username", None) if u else None


class ArticleCommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField()
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        """创建评论。"""
        request = self.context["request"]
        article: Article = self.context["article"]
        parent_id = validated_data.get("parent_id")
        parent = None
        if parent_id:
            parent = ArticleComment.objects.filter(pk=parent_id, article=article).first()
        comment = ArticleComment.objects.create(
            article=article,
            user=request.user if getattr(request.user, "is_authenticated", False) else None,
            parent=parent,
            content=validated_data["content"],
        )
        return comment
