from itertools import chain

from django.db.models import Count, Prefetch, Q
from django.utils import timezone

from blog.models import (
    Category,
    Note,
    NoteCollection,
    Post,
    Thought,
    Memory,
)


def navigation_data(request):
    published_posts = (
        Post.objects
        .filter(status=Post.Status.PUBLISHED)
        .select_related("category")
        .order_by("-published_at")
    )

    nav_categories = (
        Category.objects
        .annotate(
            published_count=Count(
                "posts",
                filter=Q(
                    posts__status=Post.Status.PUBLISHED,
                ),
            )
        )
        .prefetch_related(
            Prefetch(
                "posts",
                queryset=published_posts,
                to_attr="nav_published_posts",
            )
        )
        .order_by("name")
    )

    nav_posts = published_posts[:4]

    published_notes = (
        Note.objects
        .filter(status=Note.Status.PUBLISHED)
        .select_related(
            "author",
            "collection",
        )
        .prefetch_related("tags")
        .order_by("-published_at")
    )

    nav_note_collections = (
        NoteCollection.objects
        .annotate(
            published_count=Count(
                "notes",
                filter=Q(
                    notes__status=Note.Status.PUBLISHED,
                ),
            )
        )
        .prefetch_related(
            Prefetch(
                "notes",
                queryset=published_notes,
                to_attr="nav_published_notes",
            )
        )
        .order_by("order", "name")
    )

    nav_notes = published_notes[:4]

    nav_thoughts = (
        Thought.objects
        .filter(status=Thought.Status.PUBLISHED)
        .order_by("-published_at")[:4]
    )

    recent_activity = sorted(
        chain(
            (
                {
                    "type_name": "文稿",
                    "title": post.title,
                    "url": post.get_absolute_url(),
                    "published_at": post.published_at,
                }
                for post in nav_posts
            ),
            (
                {
                    "type_name": "手记",
                    "title": note.title,
                    "url": note.get_absolute_url(),
                    "published_at": note.published_at,
                }
                for note in nav_notes
            ),
            (
                {
                    "type_name": "思考",
                    "title": thought.content.replace("\n", " ")[:46],
                    "url": "",
                    "published_at": thought.published_at,
                }
                for thought in nav_thoughts
            ),
        ),
        key=lambda item: item["published_at"],
        reverse=True,
    )[:4]
    recent_posts = (
        Post.objects
        .filter(status=Post.Status.PUBLISHED)
        .order_by("-published_at")[:4]
    )

    recent_notes = (
        Note.objects
        .filter(status=Note.Status.PUBLISHED)
        .order_by("-published_at")[:4]
    )

    recent_memories = (
        Memory.objects
        .filter(status=Memory.Status.PUBLISHED)
        .order_by("-happened_at")[:4]
    )

    nav_timeline_items = []

    for post in recent_posts:
        nav_timeline_items.append(
            {
                "title": post.title,
                "url": post.get_absolute_url(),
                "date": post.published_at,
                "type_label": "文稿",
            }
        )

    for note in recent_notes:
        nav_timeline_items.append(
            {
                "title": note.title,
                "url": note.get_absolute_url(),
                "date": note.published_at,
                "type_label": "手记",
            }
        )

    for memory in recent_memories:
        nav_timeline_items.append(
            {
                "title": memory.title,
                "url": memory.get_absolute_url(),
                "date": memory.happened_at,
                "type_label": "回忆",
            }
        )

    nav_timeline_items = sorted(
        nav_timeline_items,
        key=lambda item: item["date"],
        reverse=True,
    )[:4]

    published_memories = Memory.objects.filter(
        status=Memory.Status.PUBLISHED,
    )

    nav_total_content_count = (
        published_posts.count()
        + published_notes.count()
        + Thought.objects.filter(
            status=Thought.Status.PUBLISHED,
        ).count()
        + published_memories.count()
    )

    nav_total_word_count = sum(
        len(content or "")
        for content in chain(
            published_posts.values_list("content", flat=True),
            published_notes.values_list("content", flat=True),
            Thought.objects.filter(
                status=Thought.Status.PUBLISHED,
            ).values_list("content", flat=True),
            published_memories.values_list("content", flat=True),
        )
    )

    first_dates = [
        value
        for value in (
            published_posts.order_by("published_at")
            .values_list("published_at", flat=True)
            .first(),
            published_notes.order_by("published_at")
            .values_list("published_at", flat=True)
            .first(),
            Thought.objects.filter(status=Thought.Status.PUBLISHED)
            .order_by("published_at")
            .values_list("published_at", flat=True)
            .first(),
            published_memories.order_by("happened_at")
            .values_list("happened_at", flat=True)
            .first(),
        )
        if value is not None
    ]

    if first_dates:
        nav_site_running_days = (
            timezone.localdate()
            - min(first_dates).date()
        ).days + 1
    else:
        nav_site_running_days = 1

    return {
        "nav_categories": nav_categories,
        "nav_posts": nav_posts,
        "nav_notes": nav_notes,
        "nav_note_collections": nav_note_collections,
        "nav_thoughts": nav_thoughts,
        "nav_recent_activity": recent_activity,
        "nav_post_count": published_posts.count(),
        "nav_note_count": published_notes.count(),
        "nav_thought_count": Thought.objects.filter(
            status=Thought.Status.PUBLISHED,
        ).count(),
        "nav_timeline_items": nav_timeline_items,
        "nav_total_content_count": nav_total_content_count,
        "nav_total_word_count": nav_total_word_count,
        "nav_site_running_days": nav_site_running_days,
    }


from django.db.models import Count
from django.urls import NoReverseMatch, reverse

from blog.models import (
    Category,
    Memory,
    Note,
    NoteCollection,
    Post,
    Tag,
    Thought,
)
from core.models import Project, Quote


def safe_reverse(
    view_name: str,
    *,
    args: list | None = None,
) -> str:
    try:
        return reverse(
            view_name,
            args=args,
        )
    except NoReverseMatch:
        return "#"


def admin_dashboard(request):
    """
    仅在 Django Admin 首页查询仪表盘数据。
    """

    if not request.user.is_authenticated:
        return {}

    if not request.user.is_staff:
        return {}

    if request.path != safe_reverse("admin:index"):
        return {}

    published_posts = Post.objects.filter(
        status=Post.Status.PUBLISHED,
    )

    draft_posts = Post.objects.filter(
        status=Post.Status.DRAFT,
    )

    published_notes = Note.objects.filter(
        status=Note.Status.PUBLISHED,
    )

    draft_notes = Note.objects.filter(
        status=Note.Status.DRAFT,
    )

    published_thoughts = Thought.objects.filter(
        status=Thought.Status.PUBLISHED,
    )

    draft_thoughts = Thought.objects.filter(
        status=Thought.Status.DRAFT,
    )

    published_memories = Memory.objects.filter(
        status=Memory.Status.PUBLISHED,
    )

    draft_memories = Memory.objects.filter(
        status=Memory.Status.DRAFT,
    )

    draft_count = sum(
        (
            draft_posts.count(),
            draft_notes.count(),
            draft_thoughts.count(),
            draft_memories.count(),
        )
    )

    total_content = sum(
        (
            Post.objects.count(),
            Note.objects.count(),
            Thought.objects.count(),
            Memory.objects.count(),
        )
    )

    dashboard_stats = [
        {
            "label": "已发布文稿",
            "value": published_posts.count(),
            "icon": "▣",
            "tone": "rose",
            "url": safe_reverse(
                "admin:blog_post_changelist",
            ),
        },
        {
            "label": "公开手记",
            "value": published_notes.count(),
            "icon": "♧",
            "tone": "green",
            "url": safe_reverse(
                "admin:blog_note_changelist",
            ),
        },
        {
            "label": "思考",
            "value": published_thoughts.count(),
            "icon": "◇",
            "tone": "blue",
            "url": safe_reverse(
                "admin:blog_thought_changelist",
            ),
        },
        {
            "label": "回忆",
            "value": published_memories.count(),
            "icon": "♥",
            "tone": "purple",
            "url": safe_reverse(
                "admin:blog_memory_changelist",
            ),
        },
        {
            "label": "全部草稿",
            "value": draft_count,
            "icon": "✎",
            "tone": "amber",
            "url": safe_reverse(
                "admin:blog_post_changelist",
            ),
        },
        {
            "label": "公开项目",
            "value": Project.objects.filter(
                is_visible=True,
            ).count(),
            "icon": "△",
            "tone": "cyan",
            "url": safe_reverse(
                "admin:core_project_changelist",
            ),
        },
        {
            "label": "一言",
            "value": Quote.objects.filter(
                is_visible=True,
            ).count(),
            "icon": "“",
            "tone": "pink",
            "url": safe_reverse(
                "admin:core_quote_changelist",
            ),
        },
        {
            "label": "分类与标签",
            "value": (
                Category.objects.count()
                + Tag.objects.count()
            ),
            "icon": "#",
            "tone": "gray",
            "url": safe_reverse(
                "admin:blog_category_changelist",
            ),
        },
    ]

    quick_actions = [
        {
            "label": "写文稿",
            "description": "创建一篇新的完整文章",
            "icon": "▣",
            "url": safe_reverse(
                "admin:blog_post_add",
            ),
        },
        {
            "label": "写手记",
            "description": "记录生活与阶段片段",
            "icon": "♧",
            "url": safe_reverse(
                "admin:blog_note_add",
            ),
        },
        {
            "label": "发思考",
            "description": "发布一条即时短内容",
            "icon": "◇",
            "url": safe_reverse(
                "admin:blog_thought_add",
            ),
        },
        {
            "label": "加回忆",
            "description": "保存值得回味的时刻",
            "icon": "♥",
            "url": safe_reverse(
                "admin:blog_memory_add",
            ),
        },
        {
            "label": "加项目",
            "description": "登记开源项目与作品",
            "icon": "△",
            "url": safe_reverse(
                "admin:core_project_add",
            ),
        },
        {
            "label": "加一言",
            "description": "保存一句值得记录的话",
            "icon": "“",
            "url": safe_reverse(
                "admin:core_quote_add",
            ),
        },
    ]

    recent_content = []

    for post in (
        published_posts
        .select_related("category")
        .order_by("-published_at")[:5]
    ):
        recent_content.append(
            {
                "title": post.title,
                "type": "文稿",
                "date": post.published_at,
                "url": safe_reverse(
                    "admin:blog_post_change",
                    args=[post.pk],
                ),
            }
        )

    for note in (
        published_notes
        .select_related("collection")
        .order_by("-published_at")[:5]
    ):
        recent_content.append(
            {
                "title": note.title,
                "type": "手记",
                "date": note.published_at,
                "url": safe_reverse(
                    "admin:blog_note_change",
                    args=[note.pk],
                ),
            }
        )

    for thought in (
        published_thoughts
        .order_by("-published_at")[:5]
    ):
        recent_content.append(
            {
                "title": (
                    thought.title
                    or thought.content[:40]
                ),
                "type": "思考",
                "date": thought.published_at,
                "url": safe_reverse(
                    "admin:blog_thought_change",
                    args=[thought.pk],
                ),
            }
        )

    for memory in (
        published_memories
        .order_by("-happened_at")[:5]
    ):
        recent_content.append(
            {
                "title": memory.title,
                "type": "回忆",
                "date": memory.happened_at,
                "url": safe_reverse(
                    "admin:blog_memory_change",
                    args=[memory.pk],
                ),
            }
        )

    recent_content.sort(
        key=lambda item: item["date"],
        reverse=True,
    )

    recent_content = recent_content[:8]

    category_distribution = list(
        Category.objects
        .annotate(
            content_count=Count("posts"),
        )
        .order_by("-content_count", "name")[:6]
    )

    collection_distribution = list(
        NoteCollection.objects
        .annotate(
            content_count=Count("notes"),
        )
        .order_by("-content_count", "order")[:6]
    )

    max_distribution = max(
        [
            item.content_count
            for item in (
                category_distribution
                + collection_distribution
            )
        ]
        or [1]
    )

    distribution = []

    for category in category_distribution:
        distribution.append(
            {
                "label": category.name,
                "kind": "文稿分类",
                "value": category.content_count,
                "percent": round(
                    category.content_count
                    / max_distribution
                    * 100,
                ),
            }
        )

    for collection in collection_distribution:
        distribution.append(
            {
                "label": collection.name,
                "kind": "手记专栏",
                "value": collection.content_count,
                "percent": round(
                    collection.content_count
                    / max_distribution
                    * 100,
                ),
            }
        )

    return {
        "dashboard_stats": dashboard_stats,
        "dashboard_quick_actions": quick_actions,
        "dashboard_recent_content": recent_content,
        "dashboard_distribution": distribution,
        "dashboard_draft_count": draft_count,
        "dashboard_total_content": total_content,
    }
