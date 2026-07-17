from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.text import slugify


class YukiContentEditorAdminMixin:
    change_form_template = "admin/yuki_content_change_form.html"
    editor_excluded_fields = (
        "slug",
        "author",
        "status",
        "published_at",
        "created_at",
        "updated_at",
        "excerpt",
    )
    editor_author_field = "author"
    editor_slug_field = "slug"
    editor_slug_source_field = "title"
    editor_status_field = "status"
    editor_published_at_field = "published_at"
    editor_publish_value = "published"
    editor_draft_value = "draft"
    editor_flag_labels = {
        "is_pinned": "置顶",
        "is_featured": "精选",
        "is_bookmarked": "重点",
    }

    def get_exclude(self, request, obj=None):
        exclude = list(
            super().get_exclude(
                request,
                obj,
            )
            or ()
        )

        for field_name in self.editor_excluded_fields:
            if self.model_has_field(field_name) and field_name not in exclude:
                exclude.append(field_name)

        for field_name in self.get_editor_flag_fields():
            if field_name not in exclude:
                exclude.append(field_name)

        return tuple(exclude)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        obj = None

        if object_id:
            obj = self.get_object(
                request,
                object_id,
            )

        extra_context["yuki_editor_flags"] = self.get_editor_flags(obj)

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context,
        )

    def save_model(self, request, obj, form, change):
        self.apply_editor_defaults(
            request,
            obj,
        )

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    def response_add(self, request, obj, post_url_continue=None):
        if self.is_yuki_editor_submit(request):
            return self.response_yuki_editor_saved(
                request,
                obj,
            )

        return super().response_add(
            request,
            obj,
            post_url_continue,
        )

    def response_change(self, request, obj):
        if self.is_yuki_editor_submit(request):
            return self.response_yuki_editor_saved(
                request,
                obj,
            )

        return super().response_change(
            request,
            obj,
        )

    def apply_editor_defaults(self, request, obj):
        if self.model_has_field(self.editor_author_field) and not getattr(
            obj,
            f"{self.editor_author_field}_id",
            None,
        ):
            setattr(
                obj,
                self.editor_author_field,
                request.user,
            )

        if self.model_has_field(self.editor_slug_field) and not getattr(
            obj,
            self.editor_slug_field,
            "",
        ):
            setattr(
                obj,
                self.editor_slug_field,
                self.build_unique_slug(obj),
            )

        if self.model_has_field(self.editor_status_field):
            if "_save_publish" in request.POST:
                setattr(
                    obj,
                    self.editor_status_field,
                    self.editor_publish_value,
                )
                self.apply_publish_time(obj)
            elif "_save_draft" in request.POST:
                setattr(
                    obj,
                    self.editor_status_field,
                    self.editor_draft_value,
                )

        for field_name in self.get_editor_flag_fields():
            setattr(
                obj,
                field_name,
                field_name in request.POST,
            )

    def apply_publish_time(self, obj):
        field_name = self.editor_published_at_field

        if not self.model_has_field(field_name):
            return

        if not getattr(
            obj,
            field_name,
            None,
        ):
            setattr(
                obj,
                field_name,
                timezone.now(),
            )

    def build_unique_slug(self, obj):
        source = getattr(
            obj,
            self.editor_slug_source_field,
            "",
        )
        base_slug = slugify(
            source,
            allow_unicode=False,
        )

        if not base_slug:
            base_slug = self.model._meta.model_name

        slug = base_slug
        index = 2
        queryset = self.model.objects.filter(
            **{self.editor_slug_field: slug}
        )

        if obj.pk:
            queryset = queryset.exclude(
                pk=obj.pk,
            )

        while queryset.exists():
            slug = f"{base_slug}-{index}"
            queryset = self.model.objects.filter(
                **{self.editor_slug_field: slug}
            )

            if obj.pk:
                queryset = queryset.exclude(
                    pk=obj.pk,
                )

            index += 1

        return slug

    def response_yuki_editor_saved(self, request, obj):
        self.message_user(
            request,
            f"{self.model._meta.verbose_name}已保存。",
            messages.SUCCESS,
        )

        return redirect(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            obj.pk,
        )

    def is_yuki_editor_submit(self, request):
        return "_save_publish" in request.POST or "_save_draft" in request.POST

    def get_editor_flags(self, obj):
        flags = []

        for field_name in self.get_editor_flag_fields():
            flags.append(
                {
                    "name": field_name,
                    "label": self.editor_flag_labels.get(
                        field_name,
                        self.get_model_field_label(field_name),
                    ),
                    "checked": bool(
                        getattr(
                            obj,
                            field_name,
                            False,
                        )
                    )
                    if obj
                    else False,
                }
            )

        return flags

    def get_editor_flag_fields(self):
        return tuple(
            field_name
            for field_name in self.editor_flag_labels
            if self.model_has_field(field_name)
        )

    def model_has_field(self, field_name):
        try:
            self.model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return False

        return True

    def get_model_field_label(self, field_name):
        try:
            return str(
                self.model._meta.get_field(field_name).verbose_name
            )
        except FieldDoesNotExist:
            return field_name.replace(
                "_",
                " ",
            )
