import json
import shutil
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

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
from core.views import SITE_PAGE_CONTENT


class Command(BaseCommand):
    help = "Export blog content to Markdown and JSON files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="content",
            help="Output directory relative to BASE_DIR. Defaults to content.",
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Remove the output directory before exporting.",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output"])

        if not output_dir.is_absolute():
            output_dir = settings.BASE_DIR / output_dir

        if options["clean"] and output_dir.exists():
            shutil.rmtree(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        counts = {
            "posts": self.export_posts(output_dir),
            "notes": self.export_notes(output_dir),
            "thoughts": self.export_thoughts(output_dir),
            "memories": self.export_memories(output_dir),
        }

        counts["data_files"] = self.export_data(output_dir)

        manifest = {
            "schema_version": 1,
            "exported_at": timezone.now().isoformat(),
            "counts": counts,
        }
        write_json(output_dir / "manifest.json", manifest)

        self.stdout.write(
            self.style.SUCCESS(
                f"Exported content to {output_dir}",
            )
        )

    def export_posts(self, output_dir: Path) -> int:
        queryset = (
            Post.objects
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("published_at", "created_at")
        )

        for post in queryset:
            front_matter = {
                "type": "post",
                "id": post.pk,
                "title": post.title,
                "slug": post.slug,
                "status": post.status,
                "excerpt": post.excerpt,
                "cover": file_name(post.cover),
                "category": related_slug(post.category),
                "tags": [
                    tag.slug
                    for tag in post.tags.all()
                ],
                "author": post.author.get_username(),
                "is_featured": post.is_featured,
                "is_pinned": post.is_pinned,
                "published_at": date_value(post.published_at),
                "created_at": date_value(post.created_at),
                "updated_at": date_value(post.updated_at),
                "url": post.get_absolute_url(),
            }
            write_markdown(
                output_dir / "posts" / f"{post.slug}.md",
                front_matter,
                post.content,
            )

        return queryset.count()

    def export_notes(self, output_dir: Path) -> int:
        queryset = (
            Note.objects
            .select_related("author", "collection")
            .prefetch_related("tags")
            .order_by("published_at", "created_at")
        )

        for note in queryset:
            front_matter = {
                "type": "note",
                "id": note.pk,
                "title": note.title,
                "slug": note.slug,
                "status": note.status,
                "excerpt": note.excerpt,
                "cover": file_name(note.cover),
                "collection": related_slug(note.collection),
                "tags": [
                    tag.slug
                    for tag in note.tags.all()
                ],
                "author": note.author.get_username(),
                "published_at": date_value(note.published_at),
                "created_at": date_value(note.created_at),
                "updated_at": date_value(note.updated_at),
                "url": note.get_absolute_url(),
            }
            write_markdown(
                output_dir / "notes" / f"{note.slug}.md",
                front_matter,
                note.content,
            )

        return queryset.count()

    def export_thoughts(self, output_dir: Path) -> int:
        queryset = (
            Thought.objects
            .select_related("author")
            .order_by("published_at", "created_at")
        )

        for thought in queryset:
            slug = (
                slugify(thought.title)
                or f"thought-{thought.pk}"
            )
            filename = (
                f"{thought.published_at:%Y-%m-%d}-{slug}.md"
                if thought.published_at
                else f"thought-{thought.pk}.md"
            )
            front_matter = {
                "type": "thought",
                "id": thought.pk,
                "title": thought.title,
                "status": thought.status,
                "image": file_name(thought.image),
                "source_title": thought.source_title,
                "source_description": thought.source_description,
                "source_url": thought.source_url,
                "source_image": file_name(thought.source_image),
                "topic": thought.topic,
                "author": thought.author.get_username(),
                "like_count": thought.like_count,
                "favorite_count": thought.favorite_count,
                "comment_count": thought.comment_count,
                "published_at": date_value(thought.published_at),
                "created_at": date_value(thought.created_at),
                "updated_at": date_value(thought.updated_at),
            }
            write_markdown(
                output_dir / "thoughts" / filename,
                front_matter,
                thought.content,
            )

        return queryset.count()

    def export_memories(self, output_dir: Path) -> int:
        queryset = Memory.objects.order_by("happened_at", "created_at")

        for memory in queryset:
            front_matter = {
                "type": "memory",
                "id": memory.pk,
                "title": memory.title,
                "slug": memory.slug,
                "status": memory.status,
                "excerpt": memory.excerpt,
                "cover": file_name(memory.cover),
                "happened_at": date_value(memory.happened_at),
                "is_bookmarked": memory.is_bookmarked,
                "created_at": date_value(memory.created_at),
                "updated_at": date_value(memory.updated_at),
                "url": memory.get_absolute_url(),
            }
            write_markdown(
                output_dir / "memories" / f"{memory.slug}.md",
                front_matter,
                memory.content,
            )

        return queryset.count()

    def export_data(self, output_dir: Path) -> int:
        data_dir = output_dir / "data"

        write_json(
            data_dir / "categories.json",
            [
                {
                    "id": category.pk,
                    "name": category.name,
                    "slug": category.slug,
                    "description": category.description,
                    "url": category.get_absolute_url(),
                }
                for category in Category.objects.order_by("name")
            ],
        )

        write_json(
            data_dir / "tags.json",
            [
                {
                    "id": tag.pk,
                    "name": tag.name,
                    "slug": tag.slug,
                    "url": tag.get_absolute_url(),
                }
                for tag in Tag.objects.order_by("name")
            ],
        )

        write_json(
            data_dir / "note_collections.json",
            [
                {
                    "id": collection.pk,
                    "name": collection.name,
                    "slug": collection.slug,
                    "description": collection.description,
                    "icon": collection.icon,
                    "order": collection.order,
                    "created_at": date_value(collection.created_at),
                    "updated_at": date_value(collection.updated_at),
                    "url": collection.get_absolute_url(),
                }
                for collection in NoteCollection.objects.order_by("order", "name")
            ],
        )

        write_json(
            data_dir / "projects.json",
            [
                {
                    "id": project.pk,
                    "name": project.name,
                    "description": project.description,
                    "github_url": project.github_url,
                    "display_date": project.display_date,
                    "icon": project.icon,
                    "order": project.order,
                    "is_visible": project.is_visible,
                    "created_at": date_value(project.created_at),
                    "updated_at": date_value(project.updated_at),
                }
                for project in Project.objects.order_by("order", "-display_date", "name")
            ],
        )

        write_json(
            data_dir / "quotes.json",
            [
                {
                    "id": quote.pk,
                    "content": quote.content,
                    "author": quote.author,
                    "source": quote.source,
                    "published_at": date_value(quote.published_at),
                    "order": quote.order,
                    "is_visible": quote.is_visible,
                    "created_at": date_value(quote.created_at),
                    "updated_at": date_value(quote.updated_at),
                }
                for quote in Quote.objects.order_by("-published_at", "order", "-created_at")
            ],
        )

        write_json(
            data_dir / "site_pages.json",
            [
                {
                    "slug": slug,
                    "title": page["title"],
                    "subtitle": page["subtitle"],
                    "url": f"/pages/{slug}/",
                }
                for slug, page in SITE_PAGE_CONTENT.items()
            ],
        )

        write_json(
            data_dir / "assets.json",
            [
                {
                    "path": media_path(path),
                    "url": f"{settings.MEDIA_URL}{media_path(path)}",
                    "size": path.stat().st_size,
                    "suffix": path.suffix.lower(),
                }
                for path in sorted(settings.MEDIA_ROOT.rglob("*"))
                if path.is_file()
            ]
            if settings.MEDIA_ROOT.exists()
            else [],
        )

        return 7


def write_markdown(path: Path, front_matter: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        + to_front_matter(front_matter)
        + "---\n\n"
        + (body or "").rstrip()
        + "\n",
        encoding="utf-8",
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def to_front_matter(data: dict[str, Any]) -> str:
    return "".join(
        f"{key}: {format_front_matter_value(value)}\n"
        for key, value in data.items()
        if not is_empty_value(value)
    )


def format_front_matter_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, int | float):
        return str(value)

    if isinstance(value, list):
        return json.dumps(
            value,
            ensure_ascii=False,
        )

    return json.dumps(
        str(value),
        ensure_ascii=False,
    )


def date_value(value) -> str:
    if value is None:
        return ""

    return value.isoformat()


def file_name(field_file) -> str:
    if not field_file:
        return ""

    return field_file.name


def related_slug(value) -> str:
    if value is None:
        return ""

    return value.slug


def is_empty_value(value: Any) -> bool:
    return value is None or value == ""


def media_path(path: Path) -> str:
    return path.relative_to(settings.MEDIA_ROOT).as_posix()
