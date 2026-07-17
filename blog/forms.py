from django import forms

from .models import Note, Post, Tag


class TagButtonSelectMultiple(
    forms.CheckboxSelectMultiple,
):
    template_name = (
        "admin/widgets/tag_button_select.html"
    )

    option_template_name = (
        "admin/widgets/tag_button_option.html"
    )


class PostAdminForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        label="标签",
        queryset=Tag.objects.all(),
        required=False,
        widget=TagButtonSelectMultiple,
        help_text="点击标签即可选择，再次点击可取消。",
    )

    class Meta:
        model = Post
        fields = "__all__"


class NoteAdminForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        label="标签",
        queryset=Tag.objects.all(),
        required=False,
        widget=TagButtonSelectMultiple,
        help_text="点击标签即可选择，再次点击可取消。",
    )

    class Meta:
        model = Note
        fields = "__all__"
