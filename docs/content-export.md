# Content Export

`python manage.py export_content --clean` exports the current Django database
content into `content/`.

The export is read-only for the database. It creates:

- `content/posts/*.md`
- `content/notes/*.md`
- `content/thoughts/*.md`
- `content/memories/*.md`
- `content/data/*.json`
- `content/manifest.json`

Markdown files use front matter plus the original body. JSON files store shared
metadata such as categories, tags, projects, quotes, site pages, and media
assets.

This directory is the bridge toward the static-site deployment plan and the
future local writing app.
