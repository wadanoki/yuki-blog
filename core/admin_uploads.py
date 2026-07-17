from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils import timezone
from django.utils.text import get_valid_filename
from django.views.decorators.http import require_POST


ALLOWED_IMAGE_EXTENSIONS = {
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".webp",
}
MAX_UPLOAD_SIZE = 8 * 1024 * 1024


@staff_member_required
@require_POST
def upload_markdown_image(request):
    image = request.FILES.get("image")

    if image is None:
        return JsonResponse(
            {
                "error": "请选择图片文件。",
            },
            status=400,
        )

    if image.size > MAX_UPLOAD_SIZE:
        return JsonResponse(
            {
                "error": "图片不能超过 8MB。",
            },
            status=400,
        )

    suffix = Path(image.name).suffix.lower()

    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        return JsonResponse(
            {
                "error": "仅支持 jpg、png、gif、webp 图片。",
            },
            status=400,
        )

    if image.content_type and not image.content_type.startswith("image/"):
        return JsonResponse(
            {
                "error": "上传的文件不是图片。",
            },
            status=400,
        )

    now = timezone.localtime()
    original_name = get_valid_filename(
        Path(image.name).stem,
    )
    filename = f"{original_name or 'image'}-{uuid4().hex[:10]}{suffix}"
    storage_path = default_storage.save(
        f"markdown/{now:%Y/%m}/{filename}",
        image,
    )
    image_url = default_storage.url(storage_path)

    return JsonResponse(
        {
            "url": image_url,
            "markdown": f"![{Path(image.name).stem}]({image_url})",
            "media_url": settings.MEDIA_URL,
        }
    )
