from django.conf import settings
from django.core.cache import (
    cache as default_cache,
    get_cache,
    InvalidCacheBackendError
)

QUAL = getattr(settings, 'VERSATILEIMAGEFIELD_JPEG_RESIZE_QUALITY', 70)

VERSATILEIMAGEFIELD_PLACEHOLDER_IMAGE = getattr(
    settings,
    'VERSATILEIMAGEFIELD_PLACEHOLDER_IMAGE',
    None
)

if not VERSATILEIMAGEFIELD_PLACEHOLDER_IMAGE:
    USE_PLACEHOLDIT = True
else:
    USE_PLACEHOLDIT = False

try:
    cache = get_cache('versatileimagefield_cache')
except InvalidCacheBackendError:
    cache = default_cache

VERSATILEIMAGEFIELD_CACHE_LENGTH = getattr(
    settings,
    'VERSATILEIMAGEFIELD_CACHE_LENGTH',
    2592000  # 30 earth days
)
