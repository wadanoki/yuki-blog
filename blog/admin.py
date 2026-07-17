from django.contrib import admin

from core.admin_cards import YukiCardListAdminMixin
from core.admin_editor import YukiContentEditorAdminMixin

from .models import (
    Category,
    Memory,
    Note,
    NoteCollection,
    Post,
    Tag,
    Thought,
)
from .forms import (
    NoteAdminForm,
    PostAdminForm,
)


@admin.register(Category)
class CategoryAdmin(YukiCardListAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }
    card_title = "分类管理"
    card_title_field = "name"
    card_excerpt_field = "description"
    card_badge_fields = ("slug",)
    card_tag_field = None


@admin.register(Tag)
class TagAdmin(YukiCardListAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }
    card_title = "标签管理"
    card_title_field = "name"
    card_badge_fields = ("slug",)
    card_tag_field = None


@admin.register(Post)
class PostAdmin(
    YukiContentEditorAdminMixin,
    YukiCardListAdminMixin,
    admin.ModelAdmin,
):
    form = PostAdminForm
    list_display = (
        "title",
        "author",
        "category",
        "status",
        "is_featured",
        "is_pinned",
        "published_at",
        "updated_at",
    )

    list_filter = ()
    search_fields = ()
    actions = None
    editor_excluded_fields = YukiContentEditorAdminMixin.editor_excluded_fields
    card_title = "文章管理"
    card_title_field = "title"
    card_excerpt_field = "excerpt"
    card_category_field = "category"
    card_badge_fields = ("status",)
    card_flag_fields = (
        "is_pinned",
        "is_featured",
    )
    card_meta_fields = (
        "author",
        "published_at",
        "updated_at",
    )

    ordering = (
        "-published_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    save_on_top = False
    fieldsets = (
        (
            "基本信息",
            {
                "fields": (
                    "title",
                    "category",
                    "tags",
                ),
            },
        ),
        (
            "文章内容",
            {
                "fields": (
                    "content",
                    "cover",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related(
            "author",
            "category",
        ).prefetch_related(
            "tags",
        )


@admin.register(Note)
class NoteAdmin(
    YukiContentEditorAdminMixin,
    YukiCardListAdminMixin,
    admin.ModelAdmin,
):
    form = NoteAdminForm
    list_display = (
        "title",
        "collection",
        "author",
        "status",
        "published_at",
        "updated_at",
    )

    card_title = "手记管理"
    card_title_field = "title"
    card_excerpt_field = "excerpt"
    card_category_field = "collection"
    card_badge_fields = ("status",)
    card_meta_fields = (
        "author",
        "published_at",
        "updated_at",
    )

    ordering = (
        "-published_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "基本信息",
            {
                "fields": (
                    "title",
                    "collection",
                    "tags",
                ),
            },
        ),
        (
            "手记内容",
            {
                "fields": (
                    "content",
                    "cover",
                ),
            },
        ),
    )


@admin.register(NoteCollection)
class NoteCollectionAdmin(YukiCardListAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "order",
        "published_note_count",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }
    card_title = "手记专栏管理"
    card_title_field = "name"
    card_excerpt_field = "description"
    card_badge_fields = ("published_note_count",)
    card_meta_fields = (
        "slug",
        "order",
        "updated_at",
    )
    card_tag_field = None

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    @admin.display(description="已发布手记")
    def published_note_count(self, obj):
        return obj.notes.filter(
            status=Note.Status.PUBLISHED,
        ).count()


@admin.register(Memory)
class MemoryAdmin(
    YukiContentEditorAdminMixin,
    YukiCardListAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "title",
        "status",
        "is_bookmarked",
        "happened_at",
        "updated_at",
    )

    card_title = "回忆管理"
    card_title_field = "title"
    card_excerpt_field = "excerpt"
    card_badge_fields = ("status",)
    card_flag_fields = ("is_bookmarked",)
    card_meta_fields = (
        "happened_at",
        "updated_at",
    )
    card_tag_field = None

    ordering = (
        "-happened_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "基本信息",
            {
                "fields": (
                    "title",
                    "happened_at",
                ),
            },
        ),
        (
            "回忆内容",
            {
                "fields": (
                    "content",
                    "cover",
                ),
            },
        ),
    )


@admin.register(Thought)
class ThoughtAdmin(
    YukiContentEditorAdminMixin,
    YukiCardListAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "short_content",
        "author",
        "status",
        "topic",
        "published_at",
        "updated_at",
    )

    card_title = "思考管理"
    card_title_field = "short_content"
    card_excerpt_field = "content"
    card_category_field = "topic"
    card_badge_fields = ("status",)
    card_meta_fields = (
        "author",
        "published_at",
        "updated_at",
    )
    card_tag_field = None

    ordering = (
        "-published_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "主要内容",
            {
                "fields": (
                    "title",
                    "content",
                    "image",
                    "topic",
                ),
            },
        ),
        (
            "外部内容卡片",
            {
                "fields": (
                    "source_title",
                    "source_description",
                    "source_url",
                    "source_image",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="内容")
    def short_content(self, obj):
        return obj.title or obj.content[:36]
