from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView

from .models import (
    Category,
    Note,
    NoteCollection,
    Post,
    Tag,
    Memory,
    Thought,
)
import math
from .services.markdown import render_markdown
from calendar import month_abbr
from dataclasses import dataclass
from itertools import chain
from datetime import timedelta
from django.core.paginator import Paginator
from django.utils import timezone


class PostListView(ListView):
    """全部文稿页面。"""

    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 8

    def get_base_queryset(self):
        return (
            Post.objects
            .filter(status=Post.Status.PUBLISHED)
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_featured_post(self):
        if not hasattr(self, "_featured_post"):
            self._featured_post = (
                self.get_base_queryset()
                .filter(is_pinned=True)
                .order_by("-published_at")
                .first()
            )

        return self._featured_post

    def get_queryset(self):
        queryset = self.get_base_queryset()

        featured_post = self.get_featured_post()

        if featured_post:
            queryset = queryset.exclude(pk=featured_post.pk)

        keyword = self.request.GET.get("q", "").strip()
        tag_slug = self.request.GET.get("tag", "").strip()
        sort = self.request.GET.get("sort", "latest")

        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword)
                | Q(excerpt__icontains=keyword)
                | Q(content__icontains=keyword)
                | Q(category__name__icontains=keyword)
                | Q(tags__name__icontains=keyword)
            ).distinct()

        if tag_slug:
            queryset = queryset.filter(
                tags__slug=tag_slug,
            )

        ordering_map = {
            "latest": ("-published_at",),
            "oldest": ("published_at",),
            "updated": ("-updated_at",),
        }

        ordering = ordering_map.get(
            sort,
            ordering_map["latest"],
        )

        return queryset.order_by(*ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        keyword = self.request.GET.get("q", "").strip()
        tag_slug = self.request.GET.get("tag", "").strip()
        sort = self.request.GET.get("sort", "latest")

        published_filter = Q(
            posts__status=Post.Status.PUBLISHED,
        )

        tags = (
            Tag.objects
            .annotate(
                published_count=Count(
                    "posts",
                    filter=published_filter,
                    distinct=True,
                )
            )
            .order_by("-published_count", "name")
        )

        active_tag = None

        if tag_slug:
            active_tag = Tag.objects.filter(
                slug=tag_slug,
            ).first()

        context.update(
            {
                "featured_post": self.get_featured_post(),
                "tags": tags,
                "active_tag": active_tag,
                "keyword": keyword,
                "current_sort": sort,
                "published_post_count": (
                    self.get_base_queryset().count()
                ),
            }
        )

        return context


class CategoryPostListView(ListView):
    """某一个分类下的全部文稿。"""

    model = Post
    template_name = "blog/category_post_list.html"
    context_object_name = "posts"

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            slug=kwargs["slug"],
        )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self):
        return (
            Post.objects
            .filter(
                status=Post.Status.PUBLISHED,
                category=self.category,
            )
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = context["posts"]

        first_post = posts.last()

        context.update(
            {
                "category": self.category,
                "category_post_count": posts.count(),
                "category_start_year": (
                    first_post.published_at.year
                    if first_post
                    else None
                ),
            }
        )

        return context


class TagPostListView(ListView):
    """某一个标签下的全部文稿。"""

    model = Post
    template_name = "blog/tag_post_list.html"
    context_object_name = "posts"

    def dispatch(self, request, *args, **kwargs):
        self.tag = get_object_or_404(
            Tag,
            slug=kwargs["slug"],
        )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self):
        return (
            Post.objects
            .filter(
                status=Post.Status.PUBLISHED,
                tags=self.tag,
            )
            .select_related(
                "author",
                "category",
            )
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = context["posts"]

        first_post = posts.last()

        category_count = (
            Category.objects
            .filter(
                posts__in=posts,
            )
            .distinct()
            .count()
        )

        context.update(
            {
                "tag": self.tag,
                "tag_post_count": posts.count(),
                "tag_category_count": category_count,
                "tag_start_year": (
                    first_post.published_at.year
                    if first_post
                    else None
                ),
            }
        )

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return (
            Post.objects
            .filter(status=Post.Status.PUBLISHED)
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        markdown_result = render_markdown(
            self.object.content,
        )

        context["post_html"] = markdown_result.html
        context["post_toc"] = markdown_result.toc

        return context


class NoteDetailView(DetailView):
    model = Note
    template_name = "blog/note_detail.html"
    context_object_name = "note"

    def get_queryset(self):
        return (
            Note.objects
            .filter(status=Note.Status.PUBLISHED)
            .select_related(
                "author",
                "collection",
            )
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        note = self.object

        markdown_result = render_markdown(
            note.content,
        )

        word_count = len(note.content.strip())

        reading_minutes = max(
            1,
            math.ceil(word_count / 500),
        )

        base_notes = (
            Note.objects
            .filter(status=Note.Status.PUBLISHED)
            .select_related("collection")
            .order_by("-published_at")
        )

        collection_notes = Note.objects.none()

        if note.collection:
            collection_notes = (
                base_notes
                .filter(collection=note.collection)
                .exclude(pk=note.pk)
            )

        previous_note = (
            base_notes
            .filter(published_at__lt=note.published_at)
            .order_by("-published_at")
            .first()
        )

        next_note = (
            base_notes
            .filter(published_at__gt=note.published_at)
            .order_by("published_at")
            .first()
        )

        context.update(
            {
                "note_html": markdown_result.html,
                "note_toc": markdown_result.toc,
                "word_count": word_count,
                "reading_minutes": reading_minutes,
                "collection_notes": collection_notes[:8],
                "recent_notes": (
                    base_notes
                    .exclude(pk=note.pk)[:6]
                ),
                "previous_note": previous_note,
                "next_note": next_note,
            }
        )

        return context


class NoteCollectionListView(ListView):
    """全部手记专栏。"""

    model = NoteCollection
    template_name = "blog/note_collection_list.html"
    context_object_name = "collections"

    def get_queryset(self):
        return (
            NoteCollection.objects
            .annotate(
                published_count=Count(
                    "notes",
                    filter=Q(
                        notes__status=Note.Status.PUBLISHED,
                    ),
                )
            )
            .order_by("order", "name")
        )


class NoteListView(ListView):
    """全部公开手记。"""

    model = Note
    template_name = "blog/note_list.html"
    context_object_name = "notes"

    def get_base_queryset(self):
        return (
            Note.objects
            .filter(status=Note.Status.PUBLISHED)
            .select_related(
                "author",
                "collection",
            )
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_queryset(self):
        featured_note = self.get_featured_note()

        queryset = self.get_base_queryset()

        if featured_note:
            queryset = queryset.exclude(
                pk=featured_note.pk,
            )

        return queryset

    def get_featured_note(self):
        if not hasattr(self, "_featured_note"):
            self._featured_note = (
                self.get_base_queryset().first()
            )

        return self._featured_note

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        collections = (
            NoteCollection.objects
            .annotate(
                published_count=Count(
                    "notes",
                    filter=Q(
                        notes__status=Note.Status.PUBLISHED,
                    ),
                )
            )
            .order_by("order", "name")
        )

        context.update(
            {
                "featured_note": self.get_featured_note(),
                "note_count": self.get_base_queryset().count(),
                "collections": collections,
            }
        )

        return context


class NoteCollectionView(ListView):
    """某个专栏下的公开手记。"""

    model = Note
    template_name = "blog/note_collection.html"
    context_object_name = "notes"

    def dispatch(self, request, *args, **kwargs):
        self.collection = get_object_or_404(
            NoteCollection,
            slug=kwargs["slug"],
        )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self):
        return (
            Note.objects
            .filter(
                status=Note.Status.PUBLISHED,
                collection=self.collection,
            )
            .select_related(
                "author",
                "collection",
            )
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        notes = context["notes"]
        latest_note = notes.first()

        context.update(
            {
                "collection": self.collection,
                "collection_note_count": notes.count(),
                "collection_latest_note": latest_note,
            }
        )

        return context


@dataclass
class TimelineItem:
    title: str
    url: str
    date: object
    type_key: str
    type_label: str
    meta: str
    excerpt: str
    is_bookmarked: bool = False


class TimelineView(TemplateView):
    """文稿、手记和回忆组成的统一时间线。"""

    template_name = "blog/timeline.html"
    paginate_by = 18

    allowed_types = {
        "all",
        "post",
        "note",
        "memory",
    }

    def get_selected_type(self) -> str:
        selected_type = self.request.GET.get(
            "type",
            "all",
        )

        if selected_type not in self.allowed_types:
            return "all"

        return selected_type

    def get_post_items(self):
        posts = (
            Post.objects
            .filter(status=Post.Status.PUBLISHED)
            .select_related("category")
            .order_by("-published_at")
        )

        return [
            TimelineItem(
                title=post.title,
                url=post.get_absolute_url(),
                date=post.published_at,
                type_key="post",
                type_label="文稿",
                meta=(
                    f"{post.category.name} · 文稿"
                    if post.category
                    else "文稿"
                ),
                excerpt=post.excerpt,
            )
            for post in posts
        ]

    def get_note_items(self):
        notes = (
            Note.objects
            .filter(status=Note.Status.PUBLISHED)
            .select_related("collection")
            .order_by("-published_at")
        )

        return [
            TimelineItem(
                title=note.title,
                url=note.get_absolute_url(),
                date=note.published_at,
                type_key="note",
                type_label="手记",
                meta=(
                    f"{note.collection.name} · 手记"
                    if note.collection
                    else "手记"
                ),
                excerpt=note.excerpt,
            )
            for note in notes
        ]

    def get_memory_items(self):
        memories = (
            Memory.objects
            .filter(status=Memory.Status.PUBLISHED)
            .order_by("-happened_at")
        )

        return [
            TimelineItem(
                title=memory.title,
                url=memory.get_absolute_url(),
                date=memory.happened_at,
                type_key="memory",
                type_label="回忆",
                meta="回忆",
                excerpt=memory.excerpt,
                is_bookmarked=memory.is_bookmarked,
            )
            for memory in memories
        ]

    def get_all_items(self):
        selected_type = self.get_selected_type()

        if selected_type == "post":
            items = self.get_post_items()

        elif selected_type == "note":
            items = self.get_note_items()

        elif selected_type == "memory":
            items = self.get_memory_items()

        else:
            items = list(
                chain(
                    self.get_post_items(),
                    self.get_note_items(),
                    self.get_memory_items(),
                )
            )

        return sorted(
            items,
            key=lambda item: item.date,
            reverse=True,
        )

    def group_page_items(self, items):
        groups = []

        for item in items:
            local_date = timezone.localtime(
                item.date,
            )

            year = local_date.year
            month = local_date.month

            if (
                    not groups
                    or groups[-1]["year"] != year
            ):
                groups.append(
                    {
                        "year": year,
                        "count": 0,
                        "months": [],
                    }
                )

            year_group = groups[-1]
            year_group["count"] += 1

            if (
                    not year_group["months"]
                    or year_group["months"][-1]["month"]
                    != month
            ):
                year_group["months"].append(
                    {
                        "month": month,
                        "month_cn": f"{month}月",
                        "month_en": month_abbr[
                            month
                        ].upper(),
                        "items": [],
                    }
                )

            year_group["months"][-1][
                "items"
            ].append(item)

        return groups

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_type = self.get_selected_type()
        all_items = self.get_all_items()

        paginator = Paginator(
            all_items,
            self.paginate_by,
        )

        page_obj = paginator.get_page(
            self.request.GET.get("page"),
        )

        now = timezone.localtime()
        start_of_year = now.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        start_of_next_year = start_of_year.replace(
            year=start_of_year.year + 1,
        )
        start_of_day = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        end_of_day = start_of_day + timezone.timedelta(
            days=1,
        )

        year_progress = (
                (now - start_of_year).total_seconds()
                / (
                        start_of_next_year
                        - start_of_year
                ).total_seconds()
                * 100
        )

        day_progress = (
                (now - start_of_day).total_seconds()
                / (
                        end_of_day
                        - start_of_day
                ).total_seconds()
                * 100
        )

        context.update(
            {
                "selected_type": selected_type,
                "page_obj": page_obj,
                "is_paginated": page_obj.has_other_pages(),
                "timeline_groups": (
                    self.group_page_items(
                        page_obj.object_list,
                    )
                ),
                "timeline_count": len(all_items),
                "day_of_year": now.timetuple().tm_yday,
                "year_progress": year_progress,
                "day_progress": day_progress,
                "current_year": now.year,
            }
        )

        return context


class MemoryDetailView(DetailView):
    model = Memory
    template_name = "blog/memory_detail.html"
    context_object_name = "memory"

    def get_queryset(self):
        return Memory.objects.filter(
            status=Memory.Status.PUBLISHED,
        )


class ThoughtListView(ListView):
    """公开思考信息流。"""

    model = Thought
    template_name = "blog/thought_list.html"
    context_object_name = "thoughts"
    paginate_by = 12

    def get_queryset(self):
        return (
            Thought.objects
            .filter(status=Thought.Status.PUBLISHED)
            .select_related("author")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["thought_count"] = (
            Thought.objects
            .filter(status=Thought.Status.PUBLISHED)
            .count()
        )

        return context
