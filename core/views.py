from datetime import date, datetime
from itertools import chain

from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from blog.models import Note, Post, Thought


def home(request):
    posts = list(
        Post.objects
        .filter(status=Post.Status.PUBLISHED)
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-is_pinned", "-published_at")[:5]
    )

    notes = list(
        Note.objects
        .filter(status=Note.Status.PUBLISHED)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-published_at")[:5]
    )

    thoughts = list(
        Thought.objects
        .filter(status=Thought.Status.PUBLISHED)
        .select_related("author")
        .order_by("-published_at")[:3]
    )

    current_year = timezone.localdate().year
    year_start = date(current_year, 1, 1)
    next_year_start = date(current_year + 1, 1, 1)

    timeline_posts = (
        Post.objects
        .filter(
            status=Post.Status.PUBLISHED,
            published_at__date__gte=year_start,
            published_at__date__lt=next_year_start,
        )
        .only("title", "slug", "published_at")
    )

    recent_items = sorted(
        chain(
            (
                {
                    "type": "post",
                    "type_name": "文稿",
                    "title": post.title,
                    "summary": (
                            post.excerpt
                            or post.content[:160]
                    ),
                    "published_at": post.published_at,
                    "url": post.get_absolute_url(),
                }
                for post in posts
            ),
            (
                {
                    "type": "note",
                    "type_name": "手记",
                    "title": note.title,
                    "summary": (
                            note.excerpt
                            or note.content[:160]
                    ),
                    "published_at": note.published_at,
                    "url": note.get_absolute_url(),
                }
                for note in notes
            ),
            (
                {
                    "type": "thought",
                    "type_name": "思考",
                    "title": "",
                    "summary": thought.content,
                    "published_at": thought.published_at,
                    "url": "",
                }
                for thought in thoughts
            ),
        ),
        key=lambda item: item["published_at"],
        reverse=True,
    )[:8]

    context = {
        "posts": posts,
        "notes": notes,
        "thoughts": thoughts,
        "recent_items": recent_items,
        "total_content_count": (
                Post.objects.filter(
                    status=Post.Status.PUBLISHED,
                ).count()
                + Note.objects.filter(
            status=Note.Status.PUBLISHED,
        ).count()
                + Thought.objects.filter(
            status=Thought.Status.PUBLISHED,
        ).count()
        ),
    }

    year_start_datetime = timezone.make_aware(
        datetime(current_year, 1, 1),
        timezone.get_current_timezone(),
    )

    next_year_datetime = timezone.make_aware(
        datetime(current_year + 1, 1, 1),
        timezone.get_current_timezone(),
    )

    year_duration = (
            next_year_datetime - year_start_datetime
    ).total_seconds()
    def get_year_position(published_at):
        elapsed = (
                published_at - year_start_datetime
        ).total_seconds()

        return max(
            0,
            min(100, elapsed / year_duration * 100),
        )

    timeline_items = []

    for post in timeline_posts:
        timeline_items.append(
            {
                "type": "post",
                "type_name": "文章",
                "title": post.title,
                "published_at": post.published_at,
                "month": post.published_at.month,
                "position": get_year_position(post.published_at),
                "url": post.get_absolute_url(),
            }
        )

    timeline_items.sort(
        key=lambda item: item["published_at"]
    )

    previous_position = None
    cluster_level = 0

    for item in timeline_items:
        if (
                previous_position is not None
                and abs(item["position"] - previous_position) < 2.4
        ):
            cluster_level = (cluster_level + 1) % 3
        else:
            cluster_level = 0

        item["level"] = cluster_level
        previous_position = item["position"]

    now = timezone.now()

    today_elapsed = (
            now - year_start_datetime
    ).total_seconds()

    today_position = max(
        0,
        min(100, today_elapsed / year_duration * 100),
    )

    context.update(
        {
            "latest_item": timeline_items[-1] if timeline_items else None,
            "timeline_items": timeline_items,
            "timeline_year": current_year,
            "today_position": today_position,
            "timeline_count": len(timeline_items),
        }
    )
    return render(request, "home/index.html", context)


from django.shortcuts import render

from .models import Project, Quote


def project_list(request):
    projects = (
        Project.objects
        .filter(is_visible=True)
        .order_by(
            "order",
            "-display_date",
            "name",
        )
    )

    return render(
        request,
        "core/project_list.html",
        {
            "projects": projects,
        },
    )


def quote_list(request):
    quotes = (
        Quote.objects
        .filter(is_visible=True)
        .order_by(
            "-published_at",
            "order",
            "-created_at",
        )
    )

    return render(
        request,
        "core/quote_list.html",
        {
            "quotes": quotes,
        },
    )


SITE_PAGE_CONTENT = {
    "about": {
        "title": "自述",
        "subtitle": "关于站长的自我介绍、经历与长期关注的主题。",
    },
    "persona": {
        "title": "人设",
        "subtitle": "用于整理公开形象、表达方式与站点中的角色设定。",
    },
    "soul": {
        "title": "灵魂",
        "subtitle": "收藏价值观、偏好，以及那些构成内在世界的片段。",
    },
    "site": {
        "title": "此站点",
        "subtitle": "介绍博客的定位、内容结构、技术栈与使用方式。",
    },
    "history": {
        "title": "历史",
        "subtitle": "记录站点与个人内容长期积累下来的时间轨迹。",
    },
    "changelog": {
        "title": "迭代",
        "subtitle": "记录博客功能、视觉与内容结构的更新。",
    },
    "guestbook": {
        "title": "留言",
        "subtitle": "用于留下问候、建议或想交流的话题。",
    },
    "friends": {
        "title": "关于友链",
        "subtitle": "友链说明、交换原则与站点收录信息。",
    },
    "consulting": {
        "title": "一对一咨询",
        "subtitle": "说明可交流的主题、合作方式与联系流程。",
    },
    "sponsor": {
        "title": "赞助",
        "subtitle": "用于说明支持站点持续维护与创作的方式。",
    },
}


def site_page(request, page_slug):
    page = SITE_PAGE_CONTENT.get(page_slug)

    if page is None:
        raise Http404("页面不存在")

    return render(
        request,
        "core/site_page.html",
        {
            "page": page,
            "page_slug": page_slug,
        },
    )
