from datetime import date, datetime

from django.contrib.admin.utils import quote
from django.core.exceptions import FieldDoesNotExist
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format


class YukiCardListAdminMixin:
    change_list_template = "admin/yuki_card_change_list.html"
    list_filter = ()
    search_fields = ()
    actions = None
    date_hierarchy = None
    list_editable = ()

    card_eyebrow = "Content Library"
    card_title = None
    card_title_field = None
    card_excerpt_field = None
    card_category_field = None
    card_badge_fields = ()
    card_flag_fields = ()
    card_meta_fields = ()
    card_tag_field = "tags"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            queryset = response.context_data["cl"].result_list
        except (AttributeError, KeyError):
            return response

        extra_context.update(
            {
                "yuki_cards": [
                    self.build_card(
                        request,
                        obj,
                    )
                    for obj in queryset
                ],
                "yuki_card_eyebrow": self.card_eyebrow,
                "yuki_card_heading": self.get_card_heading(),
            }
        )
        response.context_data.update(extra_context)

        return response

    def get_card_heading(self):
        if self.card_title:
            return self.card_title

        return f"{self.model._meta.verbose_name_plural}管理"

    def build_card(self, request, obj):
        opts = self.model._meta
        quoted_pk = quote(obj.pk)
        change_url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_change",
            args=(quoted_pk,),
            current_app=self.admin_site.name,
        )
        delete_url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_delete",
            args=(quoted_pk,),
            current_app=self.admin_site.name,
        )

        return {
            "object": obj,
            "title": self.get_card_title(obj),
            "excerpt": self.get_card_excerpt(obj),
            "category": self.get_card_category(obj),
            "badges": self.get_card_badges(obj),
            "flags": self.get_card_flags(obj),
            "meta": self.get_card_meta(obj),
            "tags": self.get_card_tags(obj),
            "change_url": change_url,
            "delete_url": delete_url,
            "can_delete": self.has_delete_permission(
                request,
                obj,
            ),
        }

    def get_card_title(self, obj):
        if self.card_title_field:
            value = self.resolve_card_value(
                obj,
                self.card_title_field,
                include_label=False,
            )

            if value:
                return value

        return str(obj)

    def get_card_excerpt(self, obj):
        if not self.card_excerpt_field:
            return ""

        return self.resolve_card_value(
            obj,
            self.card_excerpt_field,
            include_label=False,
        )

    def get_card_category(self, obj):
        if not self.card_category_field:
            return ""

        return self.resolve_card_value(
            obj,
            self.card_category_field,
            include_label=False,
        )

    def get_card_badges(self, obj):
        badges = []

        for field in self.card_badge_fields:
            value = self.resolve_card_value(
                obj,
                field,
                include_label=False,
            )

            if not value:
                continue

            badges.append(
                {
                    "label": self.get_card_label(field),
                    "value": value,
                    "modifier": self.get_card_modifier(
                        obj,
                        field,
                    ),
                }
            )

        return badges

    def get_card_flags(self, obj):
        flags = []

        for field in self.card_flag_fields:
            raw_value = getattr(
                obj,
                field,
                None,
            )

            if raw_value:
                flags.append(
                    self.get_card_label(field)
                )

        return flags

    def get_card_meta(self, obj):
        meta = []

        for field in self.card_meta_fields:
            value = self.resolve_card_value(
                obj,
                field,
                include_label=False,
            )

            if value:
                meta.append(
                    {
                        "label": self.get_card_label(field),
                        "value": value,
                    }
                )

        return meta

    def get_card_tags(self, obj):
        if not self.card_tag_field or not hasattr(
            obj,
            self.card_tag_field,
        ):
            return []

        relation = getattr(
            obj,
            self.card_tag_field,
        )

        if not hasattr(
            relation,
            "all",
        ):
            return []

        return list(relation.all()[:4])

    def get_card_modifier(self, obj, field):
        raw_value = getattr(
            obj,
            field,
            "",
        )

        return str(raw_value).lower().replace(
            "_",
            "-",
        )

    def resolve_card_value(self, obj, field, include_label=True):
        admin_value = getattr(
            self,
            field,
            None,
        )

        if callable(admin_value):
            value = admin_value(obj)
            value = self.format_card_value(value)

            if include_label and value:
                return f"{self.get_card_label(field)} {value}"

            return value

        display_getter = getattr(
            obj,
            f"get_{field}_display",
            None,
        )

        if callable(display_getter):
            value = display_getter()
        else:
            value = getattr(
                obj,
                field,
                "",
            )

            if callable(value):
                value = value()

        value = self.format_card_value(value)

        if include_label and value:
            return f"{self.get_card_label(field)} {value}"

        return value

    def format_card_value(self, value):
        if value is None or value == "":
            return ""

        if isinstance(
            value,
            bool,
        ):
            return "是" if value else "否"

        if isinstance(
            value,
            datetime,
        ):
            if timezone.is_aware(value):
                value = timezone.localtime(value)

            return date_format(
                value,
                "Y.m.d H:i",
            )

        if isinstance(
            value,
            date,
        ):
            return date_format(
                value,
                "Y.m.d",
            )

        return str(value)

    def get_card_label(self, field):
        try:
            return str(
                self.model._meta.get_field(field).verbose_name
            )
        except FieldDoesNotExist:
            pass

        attr = getattr(
            self,
            field,
            None,
        )

        if attr is not None:
            return (
                getattr(
                    attr,
                    "short_description",
                    None,
                )
                or getattr(
                    attr,
                    "description",
                    None,
                )
                or field.replace(
                    "_",
                    " ",
                )
            )

        return field.replace(
            "_",
            " ",
        )
