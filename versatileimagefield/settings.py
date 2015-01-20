from __future__ import unicode_literals

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
VERSATILEIMAGEFIELD_PLACEHOLDER_DIRNAME = '__placeholder__'
VERSATILEIMAGEFIELD_CREATE_ON_DEMAND = True

VERSATILEIMAGEFIELD_SETTINGS = {
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
    # The name of the top-level folder within your storage to save all
    # sized images. Defaults to '__sized__'
    'sized_directory_name': VERSATILEIMAGEFIELD_SIZED_DIRNAME,
    # The name of the directory to save all filtered images within.
    # Defaults to '__filtered__':
    'filtered_directory_name': VERSATILEIMAGEFIELD_FILTERED_DIRNAME,
    # The name of the directory to save placeholder images within.
    # Defaults to '__placeholder__':
    'placeholder_directory_name': VERSATILEIMAGEFIELD_PLACEHOLDER_DIRNAME,
    # Whether or not to create new images on-the-fly. Set this to `False` for
    # speedy performance but don't forget to 'pre-warm' to ensure they're
    # created and available at the appropriate URL.
    'create_images_on_demand': VERSATILEIMAGEFIELD_CREATE_ON_DEMAND
}

USER_DEFINED = getattr(
    settings,
    'VERSATILEIMAGEFIELD_SETTINGS',
    None
)

if USER_DEFINED:
    VERSATILEIMAGEFIELD_SETTINGS.update(USER_DEFINED)

QUAL = VERSATILEIMAGEFIELD_SETTINGS.get('jpeg_resize_quality')

VERSATILEIMAGEFIELD_CACHE_NAME = VERSATILEIMAGEFIELD_SETTINGS.get(
    'cache_name'
)

try:
    cache = get_cache(VERSATILEIMAGEFIELD_CACHE_NAME)
except InvalidCacheBackendError:
    cache = default_cache

VERSATILEIMAGEFIELD_CACHE_LENGTH = VERSATILEIMAGEFIELD_SETTINGS.get(
    'cache_length'
)

VERSATILEIMAGEFIELD_SIZED_DIRNAME = VERSATILEIMAGEFIELD_SETTINGS.get(
    'sized_directory_name'
)

VERSATILEIMAGEFIELD_FILTERED_DIRNAME = VERSATILEIMAGEFIELD_SETTINGS.get(
    'filtered_directory_name'
)

VERSATILEIMAGEFIELD_PLACEHOLDER_DIRNAME = VERSATILEIMAGEFIELD_SETTINGS.get(
    'placeholder_directory_name'
)

VERSATILEIMAGEFIELD_CREATE_ON_DEMAND = VERSATILEIMAGEFIELD_SETTINGS.get(
    'create_images_on_demand'
)

IMAGE_SETS = getattr(settings, 'VERSATILEIMAGEFIELD_RENDITION_KEY_SETS', {})
