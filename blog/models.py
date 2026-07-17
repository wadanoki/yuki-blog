from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """文章分类，例如：技术、生活、随笔。"""

    name = models.CharField("分类名称", max_length=50)
    slug = models.SlugField(
        "URL 标识",
        max_length=60,
        unique=True,
        help_text="建议使用英文和短横线，例如 python-notes",
    )
    description = models.TextField(
        "分类简介",
        blank=True,
    )

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse(
            "blog:category_post_list",
            kwargs={"slug": self.slug},
        )


class Tag(models.Model):
    """文章标签。"""

    name = models.CharField("标签名称", max_length=30)
    slug = models.SlugField(
        "URL 标识",
        max_length=40,
        unique=True,
    )

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse(
            "blog:tag_post_list",
            kwargs={"slug": self.slug},
        )


class Post(models.Model):
    """博客文章。"""

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"

    title = models.CharField(
        "文章标题",
        max_length=200,
    )

    slug = models.SlugField(
        "URL 标识",
        max_length=220,
        unique=True,
        help_text="建议使用英文，例如 django-blog-start",
    )

    excerpt = models.TextField(
        "文章摘要",
        max_length=500,
        blank=True,
    )

    content = models.TextField(
        "文章正文",
    )

    cover = models.ImageField(
        "封面图片",
        upload_to="posts/%Y/%m/",
        blank=True,
        null=True,
    )

    category = models.ForeignKey(
        Category,
        verbose_name="分类",
        related_name="posts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name="标签",
        related_name="posts",
        blank=True,
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        related_name="blog_posts",
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        "发布状态",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    is_featured = models.BooleanField(
        "是否精选",
        default=False,
    )

    is_pinned = models.BooleanField(
        "是否置顶",
        default=False,
    )

    published_at = models.DateTimeField(
        "发布时间",
        default=timezone.now,
    )

    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "更新时间",
        auto_now=True,
    )

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = [
            "-is_pinned",
            "-published_at",
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse(
            "blog:post_detail",
            kwargs={"slug": self.slug},
        )


class NoteCollection(models.Model):
    """手记专栏，例如近况、游记、年终总结。"""

    name = models.CharField(
        "专栏名称",
        max_length=50,
    )

    slug = models.SlugField(
        "URL 标识",
        max_length=60,
        unique=True,
        help_text="建议使用英文、小写字母和短横线",
    )

    description = models.TextField(
        "专栏简介",
        blank=True,
    )

    icon = models.CharField(
        "图标",
        max_length=20,
        blank=True,
        help_text="可以填写一个 Emoji，例如：🍵",
    )

    order = models.PositiveIntegerField(
        "排序",
        default=0,
        help_text="数字越小越靠前",
    )

    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "更新时间",
        auto_now=True,
    )

    class Meta:
        verbose_name = "手记专栏"
        verbose_name_plural = "手记专栏"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse(
            "blog:note_collection",
            kwargs={"slug": self.slug},
        )


class Note(models.Model):
    """较短但具有独立主题的手记。"""

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"

    title = models.CharField(
        "手记标题",
        max_length=200,
    )

    slug = models.SlugField(
        "URL 标识",
        max_length=220,
        unique=True,
        help_text="建议使用英文和短横线",
    )

    excerpt = models.TextField(
        "摘要",
        max_length=300,
        blank=True,
    )

    content = models.TextField(
        "手记正文",
    )

    cover = models.ImageField(
        "配图",
        upload_to="notes/%Y/%m/",
        blank=True,
        null=True,
    )

    collection = models.ForeignKey(
        NoteCollection,
        verbose_name="所属专栏",
        related_name="notes",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name="标签",
        related_name="notes",
        blank=True,
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        related_name="blog_notes",
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        "发布状态",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    published_at = models.DateTimeField(
        "发布时间",
        default=timezone.now,
    )

    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "更新时间",
        auto_now=True,
    )

    class Meta:
        verbose_name = "手记"
        verbose_name_plural = "手记"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse(
            "blog:note_detail",
            kwargs={"slug": self.slug},
        )


class Thought(models.Model):
    """短内容、碎念与即时思考。"""

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"

    content = models.TextField(
        "正文",
    )

    title = models.CharField(
        "标题",
        max_length=200,
        blank=True,
    )

    image = models.ImageField(
        "配图",
        upload_to="thoughts/%Y/%m/",
        blank=True,
        null=True,
    )

    source_title = models.CharField(
        "外部内容标题",
        max_length=200,
        blank=True,
    )

    source_description = models.TextField(
        "外部内容简介",
        blank=True,
    )

    source_url = models.URLField(
        "外部链接",
        blank=True,
    )

    source_image = models.ImageField(
        "外部内容封面",
        upload_to="thoughts/sources/%Y/%m/",
        blank=True,
        null=True,
    )

    topic = models.CharField(
        "话题",
        max_length=80,
        blank=True,
        help_text="例如：回头看见自己",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        related_name="blog_thoughts",
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        "发布状态",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    like_count = models.PositiveIntegerField(
        "喜欢数",
        default=0,
    )

    favorite_count = models.PositiveIntegerField(
        "收藏数",
        default=0,
    )

    comment_count = models.PositiveIntegerField(
        "评论数",
        default=0,
    )

    published_at = models.DateTimeField(
        "发布时间",
        default=timezone.now,
    )

    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "更新时间",
        auto_now=True,
    )

    class Meta:
        verbose_name = "思考"
        verbose_name_plural = "思考"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title or self.content[:30]


class Memory(models.Model):
    """值得回味的片段、照片或往事。"""

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"

    title = models.CharField(
        "标题",
        max_length=200,
    )

    slug = models.SlugField(
        "URL 标识",
        max_length=220,
        unique=True,
    )

    excerpt = models.TextField(
        "摘要",
        max_length=400,
        blank=True,
    )

    content = models.TextField(
        "正文",
        blank=True,
    )

    cover = models.ImageField(
        "图片",
        upload_to="memories/%Y/%m/",
        blank=True,
        null=True,
    )

    happened_at = models.DateTimeField(
        "发生时间",
        default=timezone.now,
        help_text="这段回忆实际发生的时间。",
    )

    is_bookmarked = models.BooleanField(
        "重点回忆",
        default=False,
    )

    status = models.CharField(
        "发布状态",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "更新时间",
        auto_now=True,
    )

    class Meta:
        verbose_name = "回忆"
        verbose_name_plural = "回忆"
        ordering = ["-happened_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse(
            "blog:memory_detail",
            kwargs={"slug": self.slug},
        )
