from django.conf import settings
from django.core.cache import (
    cache as default_cache,
    get_cache,
    InvalidCacheBackendError
)

QUAL = getattr(settings, 'SIZEDIMAGEFIELD_JPEG_RESIZE_QUALITY', 70)

SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE = getattr(
    settings,
    'SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE',
    None
)

if not SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE:
    USE_PLACEHOLDIT = True
else:
    USE_PLACEHOLDIT = False

try:
    cache = get_cache('sizedimagefield_cache')
except InvalidCacheBackendError:
    cache = default_cache

SIZEDIMAGEFIELD_CACHE_LENGTH = getattr(
    settings,
    'SIZEDIMAGEFIELD_CACHE_LENGTH',
    2592000
)
