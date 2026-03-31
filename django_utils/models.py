from django.conf import settings
from django.db import models


class UserFile(models.Model):
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    original_name = models.CharField(max_length=255)
    size = models.BigIntegerField(default=0)
    content_type = models.CharField(max_length=127, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"UserFile(id={self.id}, original_name={self.original_name})"


class OperationLog(models.Model):
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operation_logs",
        verbose_name="操作用户",
        db_comment="触发本次操作的用户",
    )
    action = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name="动作",
        db_comment="动作标识（如 file_upload / admin_user_create）",
    )
    remark = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="中文备注",
        db_comment="便于运营/排查的中文备注",
    )
    path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="请求路径",
        db_comment="HTTP 请求路径",
    )
    method = models.CharField(
        max_length=10,
        blank=True,
        default="",
        verbose_name="请求方法",
        db_comment="HTTP 方法",
    )
    ip = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="客户端IP",
        db_comment="客户端 IP（优先 X-Forwarded-For）",
    )
    status_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="HTTP状态码",
        db_comment="HTTP 响应状态码",
    )
    response_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="业务码",
        db_comment="统一返回结构中的 code（如 20001）",
    )
    success = models.BooleanField(
        default=True,
        verbose_name="是否成功",
        db_comment="根据 HTTP 状态码与业务码推断",
    )
    detail = models.TextField(
        blank=True,
        default="",
        verbose_name="详情",
        db_comment="异常信息或补充说明",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="日志创建时间",
    )

    class Meta:
        verbose_name = "操作日志"
        verbose_name_plural = "操作日志"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"OperationLog(id={self.id}, action={self.action}, operator_id={self.operator_id})"


class ArticleCategory(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="分类名称",
        db_comment="文章分类名称（唯一）",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="分类描述",
        db_comment="分类说明",
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name="排序",
        db_comment="数字越小越靠前",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        db_comment="是否在用户端展示",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="创建时间",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间",
        db_comment="更新时间",
    )

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = "文章分类"
        ordering = ["sort_order", "-id"]

    def __str__(self) -> str:
        """返回分类可读字符串。"""
        return f"ArticleCategory(id={self.id}, name={self.name})"


class Article(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "草稿"),
        (STATUS_PUBLISHED, "已发布"),
        (STATUS_ARCHIVED, "已归档"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="作者",
        db_comment="文章作者（管理员编辑时可为空）",
    )
    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="分类",
        db_comment="文章分类",
    )
    cover = models.FileField(
        upload_to="articles/covers/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name="封面",
        db_comment="封面文件（使用 FileField 避免依赖 Pillow）",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="标题",
        db_comment="文章标题",
    )
    summary = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="摘要",
        db_comment="文章摘要（可选）",
    )
    content = models.TextField(
        blank=True,
        default="",
        verbose_name="内容",
        db_comment="文章正文内容",
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name="状态",
        db_comment="草稿/发布/归档",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="发布时间",
        db_comment="发布时刻（仅发布状态有效）",
    )
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name="浏览数",
        db_comment="文章浏览次数（可选统计）",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="创建时间",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间",
        db_comment="更新时间",
    )

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-id"]

    def __str__(self) -> str:
        """返回文章可读字符串。"""
        return f"Article(id={self.id}, title={self.title})"


class ArticleComment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="文章",
        db_comment="评论所属文章",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="article_comments",
        verbose_name="评论用户",
        db_comment="发表评论的用户（允许匿名为空）",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="父评论",
        db_comment="回复目标评论（可为空）",
    )
    content = models.TextField(
        verbose_name="评论内容",
        db_comment="评论正文",
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="是否删除",
        db_comment="软删除标记（用户端不展示）",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="评论创建时间",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间",
        db_comment="评论更新时间",
    )

    class Meta:
        verbose_name = "文章评论"
        verbose_name_plural = "文章评论"
        ordering = ["-id"]

    def __str__(self) -> str:
        """返回评论可读字符串。"""
        return f"ArticleComment(id={self.id}, article_id={self.article_id}, user_id={self.user_id})"


class ArticleLike(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="文章",
        db_comment="点赞所属文章",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_likes",
        verbose_name="点赞用户",
        db_comment="点赞的用户",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="点赞时间",
    )

    class Meta:
        verbose_name = "文章点赞"
        verbose_name_plural = "文章点赞"
        constraints = [
            models.UniqueConstraint(fields=["article", "user"], name="uniq_article_like"),
        ]
        ordering = ["-id"]

    def __str__(self) -> str:
        """返回点赞可读字符串。"""
        return f"ArticleLike(id={self.id}, article_id={self.article_id}, user_id={self.user_id})"


class ArticleFavorite(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="文章",
        db_comment="收藏所属文章",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_favorites",
        verbose_name="收藏用户",
        db_comment="收藏的用户",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="收藏时间",
    )

    class Meta:
        verbose_name = "文章收藏"
        verbose_name_plural = "文章收藏"
        constraints = [
            models.UniqueConstraint(fields=["article", "user"], name="uniq_article_favorite"),
        ]
        ordering = ["-id"]

    def __str__(self) -> str:
        """返回收藏可读字符串。"""
        return f"ArticleFavorite(id={self.id}, article_id={self.article_id}, user_id={self.user_id})"

