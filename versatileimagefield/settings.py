from django.conf import settings
from django.core.cache import (
    cache as default_cache,
    get_cache,
    InvalidCacheBackendError
)

# Defaults
QUAL = 70
VERSATILEIMAGEFIELD_CACHE_LENGTH = 2592000
VERSATILEIMAGEFIELD_CACHE_NAME = 'versatileimagefield_cache'
VERSATILEIMAGEFIELD_SIZED_DIRNAME = '__sized__'
VERSATILEIMAGEFIELD_FILTERED_DIRNAME = '__filtered__'

DEFAULTS = {
    # The amount of time, in seconds, that references to created images
    # should be stored in the cache. Defaults to `2592000` (30 days)
    'cache_length': VERSATILEIMAGEFIELD_CACHE_LENGTH,
    # The name of the cache you'd like `django-versatileimagefield` to use.
    # Defaults to 'versatileimagefield_cache'. If no cache exists to the name
    # provided, the 'default' cache will be used.
    'cache_name': VERSATILEIMAGEFIELD_CACHE_NAME,
    # The save quality of modified JPEG images. More info here:
    # http://pillow.readthedocs.org/en/latest/handbook/image-file-formats.html#jpeg
    # Defaults to 70
    'jpeg_resize_quality': QUAL,
    # A path on disc to an image that will be used as a 'placeholder'
    # for non-existant images.
    # If 'global_placeholder_image' is unset, the excellent, free-to-use
    # http://placehold.it service will be used instead.
    'global_placeholder_image': None,
    # The name of the top-level folder within your storage to save all
    # sized images. Defaults to '__sized__'
    'sized_directory_name': VERSATILEIMAGEFIELD_SIZED_DIRNAME,
    # The name of the directory to save all filtered images within.
    # Defaults to '__filtered__':
    'filtered_directory_name': VERSATILEIMAGEFIELD_FILTERED_DIRNAME
}

SETTINGS = getattr(
    settings,
    'VERSATILEIMAGEFIELD_SETTINGS',
    DEFAULTS
)

QUAL = SETTINGS.get('jpeg_resize_quality', QUAL)

VERSATILEIMAGEFIELD_PLACEHOLDER_IMAGE = SETTINGS.get(
    'global_placeholder_image',
    None
)

if not VERSATILEIMAGEFIELD_PLACEHOLDER_IMAGE:
    USE_PLACEHOLDIT = True
else:
    USE_PLACEHOLDIT = False

VERSATILEIMAGEFIELD_CACHE_NAME = SETTINGS.get(
    'cache_name',
    VERSATILEIMAGEFIELD_CACHE_NAME
)

try:
    cache = get_cache(VERSATILEIMAGEFIELD_CACHE_NAME)
except InvalidCacheBackendError:
    cache = default_cache

VERSATILEIMAGEFIELD_CACHE_LENGTH = SETTINGS.get(
    'cache_length',
    VERSATILEIMAGEFIELD_CACHE_LENGTH
)

VERSATILEIMAGEFIELD_SIZED_DIRNAME = SETTINGS.get(
    'sized_directory_name',
    VERSATILEIMAGEFIELD_SIZED_DIRNAME
)

VERSATILEIMAGEFIELD_FILTERED_DIRNAME = SETTINGS.get(
    'filtered_directory_name',
    VERSATILEIMAGEFIELD_FILTERED_DIRNAME
)
