import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

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


class Command(BaseCommand):
    help = "Import blog content from Markdown and JSON files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            default="content",
            help="Input directory relative to BASE_DIR. Defaults to content.",
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Remove imported content before importing.",
        )

    def handle(self, *args, **options):
        input_dir = Path(options["input"])

        if not input_dir.is_absolute():
            input_dir = settings.BASE_DIR / input_dir

        if not input_dir.exists():
            raise CommandError(f"Content directory does not exist: {input_dir}")

        if options["clean"]:
            self.clean_content()

        counts = {
            "categories": self.import_categories(input_dir),
            "tags": self.import_tags(input_dir),
            "note_collections": self.import_note_collections(input_dir),
            "projects": self.import_projects(input_dir),
            "quotes": self.import_quotes(input_dir),
            "posts": self.import_posts(input_dir),
            "notes": self.import_notes(input_dir),
            "thoughts": self.import_thoughts(input_dir),
            "memories": self.import_memories(input_dir),
        }

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported content from {input_dir}: {counts}",
            )
        )

    def clean_content(self) -> None:
        Post.objects.all().delete()
        Note.objects.all().delete()
        Thought.objects.all().delete()
        Memory.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        NoteCollection.objects.all().delete()
        Project.objects.all().delete()
        Quote.objects.all().delete()

    def import_categories(self, input_dir: Path) -> int:
        items = read_json(input_dir / "data" / "categories.json", [])

        for item in items:
            Category.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item.get("name") or item["slug"],
                    "description": item.get("description", ""),
                },
            )

        return len(items)

    def import_tags(self, input_dir: Path) -> int:
        items = read_json(input_dir / "data" / "tags.json", [])

        for item in items:
            Tag.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item.get("name") or item["slug"],
                },
            )

        return len(items)

    def import_note_collections(self, input_dir: Path) -> int:
        items = read_json(input_dir / "data" / "note_collections.json", [])

        for item in items:
            collection, _ = NoteCollection.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item.get("name") or item["slug"],
                    "description": item.get("description", ""),
                    "icon": item.get("icon", ""),
                    "order": item.get("order", 0),
                },
            )
            restore_timestamps(collection, item)

        return len(items)

    def import_projects(self, input_dir: Path) -> int:
        items = read_json(input_dir / "data" / "projects.json", [])

        for item in items:
            project, _ = Project.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item.get("description", ""),
                    "github_url": item.get("github_url", ""),
                    "display_date": item.get("display_date", ""),
                    "icon": item.get("icon", ""),
                    "order": item.get("order", 0),
                    "is_visible": item.get("is_visible", True),
                },
            )
            restore_timestamps(project, item)

        return len(items)

    def import_quotes(self, input_dir: Path) -> int:
        items = read_json(input_dir / "data" / "quotes.json", [])

        for item in items:
            quote, _ = Quote.objects.update_or_create(
                content=item["content"],
                defaults={
                    "author": item.get("author", ""),
                    "source": item.get("source", ""),
                    "published_at": parse_dt(item.get("published_at")),
                    "order": item.get("order", 0),
                    "is_visible": item.get("is_visible", True),
                },
            )
            restore_timestamps(quote, item)

        return len(items)

    def import_posts(self, input_dir: Path) -> int:
        count = 0

        for path in sorted((input_dir / "posts").glob("*.md")):
            data, body = read_markdown(path)
            author = get_author(data.get("author"))
            category = get_by_slug(Category, data.get("category"))
            post, _ = Post.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data.get("title") or data["slug"],
                    "excerpt": data.get("excerpt", ""),
                    "content": body,
                    "cover": data.get("cover", ""),
                    "category": category,
                    "author": author,
                    "status": data.get("status", Post.Status.DRAFT),
                    "is_featured": data.get("is_featured", False),
                    "is_pinned": data.get("is_pinned", False),
                    "published_at": parse_dt(data.get("published_at")),
                },
            )
            post.tags.set(Tag.objects.filter(slug__in=data.get("tags", [])))
            restore_timestamps(post, data)
            count += 1

        return count

    def import_notes(self, input_dir: Path) -> int:
        count = 0

        for path in sorted((input_dir / "notes").glob("*.md")):
            data, body = read_markdown(path)
            author = get_author(data.get("author"))
            collection = get_by_slug(NoteCollection, data.get("collection"))
            note, _ = Note.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data.get("title") or data["slug"],
                    "excerpt": data.get("excerpt", ""),
                    "content": body,
                    "cover": data.get("cover", ""),
                    "collection": collection,
                    "author": author,
                    "status": data.get("status", Note.Status.DRAFT),
                    "published_at": parse_dt(data.get("published_at")),
                },
            )
            note.tags.set(Tag.objects.filter(slug__in=data.get("tags", [])))
            restore_timestamps(note, data)
            count += 1

        return count

    def import_thoughts(self, input_dir: Path) -> int:
        count = 0

        for path in sorted((input_dir / "thoughts").glob("*.md")):
            data, body = read_markdown(path)
            author = get_author(data.get("author"))
            thought, _ = Thought.objects.update_or_create(
                title=data.get("title", ""),
                content=body,
                defaults={
                    "image": data.get("image", ""),
                    "source_title": data.get("source_title", ""),
                    "source_description": data.get("source_description", ""),
                    "source_url": data.get("source_url", ""),
                    "source_image": data.get("source_image", ""),
                    "topic": data.get("topic", ""),
                    "author": author,
                    "status": data.get("status", Thought.Status.DRAFT),
                    "like_count": data.get("like_count", 0),
                    "favorite_count": data.get("favorite_count", 0),
                    "comment_count": data.get("comment_count", 0),
                    "published_at": parse_dt(data.get("published_at")),
                },
            )
            restore_timestamps(thought, data)
            count += 1

        return count

    def import_memories(self, input_dir: Path) -> int:
        count = 0

        for path in sorted((input_dir / "memories").glob("*.md")):
            data, body = read_markdown(path)
            memory, _ = Memory.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data.get("title") or data["slug"],
                    "excerpt": data.get("excerpt", ""),
                    "content": body,
                    "cover": data.get("cover", ""),
                    "happened_at": parse_dt(data.get("happened_at")),
                    "is_bookmarked": data.get("is_bookmarked", False),
                    "status": data.get("status", Memory.Status.DRAFT),
                },
            )
            restore_timestamps(memory, data)
            count += 1

        return count


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    return json.loads(path.read_text(encoding="utf-8"))


def read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")

    if not text.startswith("---\n"):
        return {}, text

    _, front_matter, body = text.split("---\n", 2)
    return parse_front_matter(front_matter), body.lstrip("\n")


def parse_front_matter(text: str) -> dict[str, Any]:
    data = {}

    for line in text.splitlines():
        if not line.strip() or ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        raw_value = raw_value.strip()

        if raw_value in {"true", "false"}:
            value = raw_value == "true"
        else:
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError:
                value = raw_value

        data[key.strip()] = value

    return data


def parse_dt(value: Any):
    if not value:
        return timezone.now()

    parsed = parse_datetime(str(value))

    if parsed is None:
        return timezone.now()

    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed)

    return parsed


def get_author(username: str | None):
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username or "yuki",
    )

    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])

    return user


def get_by_slug(model, slug: str | None):
    if not slug:
        return None

    return model.objects.filter(slug=slug).first()


def restore_timestamps(instance, data: dict[str, Any]) -> None:
    updates = {}

    if data.get("created_at"):
        updates["created_at"] = parse_dt(data["created_at"])

    if data.get("updated_at"):
        updates["updated_at"] = parse_dt(data["updated_at"])

    if updates:
        instance.__class__.objects.filter(pk=instance.pk).update(**updates)
