from django.contrib import admin

from .admin_cards import YukiCardListAdminMixin
from .models import Project, Quote


@admin.register(Project)
class ProjectAdmin(YukiCardListAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "display_date",
        "order",
        "is_visible",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    card_title = "项目管理"
    card_title_field = "name"
    card_excerpt_field = "description"
    card_badge_fields = ("is_visible",)
    card_flag_fields = ("is_visible",)
    card_meta_fields = (
        "display_date",
        "order",
        "updated_at",
    )
    card_tag_field = None


@admin.register(Quote)
class QuoteAdmin(YukiCardListAdminMixin, admin.ModelAdmin):
    list_display = (
        "short_content",
        "author",
        "source",
        "published_at",
        "order",
        "is_visible",
    )

    ordering = (
        "-published_at",
        "order",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    card_title = "一言管理"
    card_title_field = "short_content"
    card_excerpt_field = "content"
    card_category_field = "source"
    card_badge_fields = ("is_visible",)
    card_flag_fields = ("is_visible",)
    card_meta_fields = (
        "author",
        "published_at",
        "order",
    )
    card_tag_field = None

    @admin.display(description="内容")
    def short_content(self, obj):
        return obj.content[:48]
