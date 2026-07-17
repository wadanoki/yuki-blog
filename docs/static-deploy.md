# Static Deploy

Build a static snapshot:

```bash
pnpm run build:static
```

The deployable directory is `public/`.

Cloudflare Pages settings:

- Build command: `pnpm run build:pages`
- Build output directory: `public`
- Python version: use a version compatible with this project's Django release.
- Package manager: pnpm

Current limitations:

- Static output is generated from Django views and the current database.
- Admin pages are not included.
- Pagination beyond the first page is not generated yet.
- Search/filter forms render, but static hosting cannot process dynamic query
  searches unless the target page was prebuilt.
- Site info pages still use placeholder content until edited in Django.
