from django.db import models


class Project(models.Model):
    name = models.CharField(
        "项目名称",
        max_length=120,
    )

    description = models.TextField(
        "项目简介",
        blank=True,
    )

    github_url = models.URLField(
        "GitHub 地址",
    )

    display_date = models.CharField(
        "展示日期",
        max_length=20,
        blank=True,
        help_text="例如：2026.06",
    )

    icon = models.CharField(
        "图标",
        max_length=20,
        blank=True,
        help_text="可填写 Emoji，例如：📦",
    )

    order = models.PositiveIntegerField(
        "排序",
        default=0,
        help_text="数字越小越靠前",
    )

    is_visible = models.BooleanField(
        "是否显示",
        default=True,
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
        verbose_name = "项目"
        verbose_name_plural = "项目"
        ordering = (
            "order",
            "-display_date",
            "name",
        )

    def __str__(self) -> str:
        return self.name


class Quote(models.Model):
    content = models.TextField(
        "一言内容",
    )

    author = models.CharField(
        "作者",
        max_length=120,
        blank=True,
    )

    source = models.CharField(
        "出处",
        max_length=200,
        blank=True,
        help_text="例如：出自《人间失格》",
    )

    published_at = models.DateTimeField(
        "展示日期",
    )

    order = models.PositiveIntegerField(
        "排序",
        default=0,
        help_text="数字越小越靠前；日期相同时生效",
    )

    is_visible = models.BooleanField(
        "是否显示",
        default=True,
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
        verbose_name = "一言"
        verbose_name_plural = "一言"
        ordering = (
            "-published_at",
            "order",
            "-created_at",
        )

    def __str__(self) -> str:
        return self.content[:36]
