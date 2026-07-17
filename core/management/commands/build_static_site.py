import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.test import Client
from django.utils import timezone

from blog.models import (
    Category,
    Memory,
    Note,
    NoteCollection,
    Post,
    Tag,
)


@dataclass(frozen=True)
class StaticPage:
    path: str
    output: str


class Command(BaseCommand):
    help = "Build a static HTML snapshot of the public site."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="public",
            help="Output directory relative to BASE_DIR. Defaults to public.",
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Remove the output directory before building.",
        )
        parser.add_argument(
            "--skip-assets",
            action="store_true",
            help="Only render HTML. Do not copy static and media assets.",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output"])

        if not output_dir.is_absolute():
            output_dir = settings.BASE_DIR / output_dir

        if options["clean"] and output_dir.exists():
            shutil.rmtree(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        if not options["skip_assets"]:
            self.copy_assets(output_dir)

        pages = self.get_pages()
        client = Client(
            HTTP_HOST=settings.ALLOWED_HOSTS[0],
        )
        rendered = []

        for page in pages:
            response = client.get(page.path)

            if response.status_code != 200:
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping {page.path}: HTTP {response.status_code}",
                    )
                )
                continue

            output_path = output_dir / page.output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)
            rendered.append(
                {
                    "path": page.path,
                    "output": page.output,
                }
            )

        self.write_not_found(output_dir)
        self.write_manifest(output_dir, rendered)

        self.stdout.write(
            self.style.SUCCESS(
                f"Built {len(rendered)} pages into {output_dir}",
            )
        )

    def get_pages(self) -> list[StaticPage]:
        pages = [
            page("/", "index.html"),
            page("/blog/", "blog/index.html"),
            page("/blog/notes/", "blog/notes/index.html"),
            page("/blog/notes/collections/", "blog/notes/collections/index.html"),
            page("/blog/timeline/", "blog/timeline/index.html"),
            page("/blog/timeline/?type=note", "blog/timeline/type/note/index.html"),
            page("/blog/timeline/?type=post", "blog/timeline/type/post/index.html"),
            page("/blog/timeline/?type=memory", "blog/timeline/type/memory/index.html"),
            page("/blog/thoughts/", "blog/thoughts/index.html"),
            page("/projects/", "projects/index.html"),
            page("/quotes/", "quotes/index.html"),
            page("/pages/about/", "pages/about/index.html"),
            page("/pages/soul/", "pages/soul/index.html"),
            page("/pages/site/", "pages/site/index.html"),
            page("/pages/guestbook/", "pages/guestbook/index.html"),
        ]

        pages.extend(
            page(
                category.get_absolute_url(),
                f"blog/category/{category.slug}/index.html",
            )
            for category in Category.objects.filter(
                posts__status=Post.Status.PUBLISHED,
            ).distinct()
        )

        pages.extend(
            page(
                tag.get_absolute_url(),
                f"blog/tag/{tag.slug}/index.html",
            )
            for tag in Tag.objects.filter(
                posts__status=Post.Status.PUBLISHED,
            ).distinct()
        )

        pages.extend(
            page(
                collection.get_absolute_url(),
                f"blog/notes/collection/{collection.slug}/index.html",
            )
            for collection in NoteCollection.objects.filter(
                notes__status=Note.Status.PUBLISHED,
            ).distinct()
        )

        pages.extend(
            page(
                post.get_absolute_url(),
                f"blog/{post.slug}/index.html",
            )
            for post in Post.objects.filter(
                status=Post.Status.PUBLISHED,
            )
        )

        pages.extend(
            page(
                note.get_absolute_url(),
                f"blog/notes/{note.slug}/index.html",
            )
            for note in Note.objects.filter(
                status=Note.Status.PUBLISHED,
            )
        )

        pages.extend(
            page(
                memory.get_absolute_url(),
                f"blog/memories/{memory.slug}/index.html",
            )
            for memory in Memory.objects.filter(
                status=Memory.Status.PUBLISHED,
            )
        )

        return pages

    def copy_assets(self, output_dir: Path) -> None:
        static_output_dir = output_dir / settings.STATIC_URL.strip("/")

        if static_output_dir.exists():
            shutil.rmtree(static_output_dir)

        call_command(
            "collectstatic",
            interactive=False,
            verbosity=0,
        )

        shutil.copytree(
            settings.STATIC_ROOT,
            static_output_dir,
        )

        media_output_dir = output_dir / settings.MEDIA_URL.strip("/")

        if media_output_dir.exists():
            shutil.rmtree(media_output_dir)

        if settings.MEDIA_ROOT.exists():
            shutil.copytree(
                settings.MEDIA_ROOT,
                media_output_dir,
            )

    def write_not_found(self, output_dir: Path) -> None:
        not_found = output_dir / "404.html"
        not_found.write_text(
            "<!doctype html><meta charset=\"utf-8\">"
            "<title>页面不存在 - Yuki Blog</title>"
            "<main style=\"font-family:system-ui;padding:48px\">"
            "<h1>页面不存在</h1>"
            "<p>这个地址还没有内容。</p>"
            "<p><a href=\"/\">返回首页</a></p>"
            "</main>",
            encoding="utf-8",
        )

    def write_manifest(self, output_dir: Path, rendered: list[dict]) -> None:
        manifest = {
            "schema_version": 1,
            "built_at": timezone.now().isoformat(),
            "page_count": len(rendered),
            "pages": rendered,
        }
        (output_dir / "static-manifest.json").write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def page(path: str, output: str) -> StaticPage:
    return StaticPage(
        path=path,
        output=output,
    )
