from django.core.exceptions import ValidationError

ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"}


def validate_video_url(value):
    """Валидатор: разрешаем только ссылки на youtube.com."""
    from urllib.parse import urlparse

    parsed = urlparse(value)

    if parsed.scheme not in ("http", "https"):
        raise ValidationError(
            "Ссылка должна начинаться с http:// или https://"
        )

    host = parsed.netloc.lower()
    if host not in ALLOWED_HOSTS:
        raise ValidationError(
            f"Разрешены только ссылки на youtube.com. "
            f"Получено: '{host or value}' — этот ресурс запрещён."
        )