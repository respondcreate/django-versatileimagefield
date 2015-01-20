from __future__ import unicode_literals

from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from ..settings import (
    QUAL,
    cache,
    VERSATILEIMAGEFIELD_CACHE_LENGTH
)
from ..utils import get_resized_path
from .base import ProcessedImage


class MalformedSizedImageKey(Exception):
    pass


@python_2_unicode_compatible
class SizedImageInstance(object):
    """
    A simple class for returning paths-on-storage and URLs
    associated with images created by SizedImage
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __str__(self):
        return self.url


class SizedImage(ProcessedImage, dict):
    """
    A dict subclass that exposes an image sizing API via key access.
    Subclasses must implement a `process_image` method.

    See versatileimagefield.versatileimagefield.CroppedImage and
    versatileimagefield.versatileimagefield.ThumbnailImage for subclass
    examples.
    """

    def __init__(self, path_to_image, storage, create_on_demand, ppoi=None):
        super(SizedImage, self).__init__(
            path_to_image, storage, create_on_demand
        )
        self.ppoi = ppoi
        try:
            key = self.get_filename_key()
        except AttributeError:
            raise NotImplementedError(
                'SizedImage subclasses must define a'
                ' `filename_key` attribute or override the '
                '`get_filename_key` method.'
            )
        else:
            del key

    def get_filename_key(self):
        """
        Returns a string that will be used to identify the resized image.
        """
        return self.filename_key

    def __setitem__(self, key, value):
        raise NotImplementedError(
            '%s instances do not allow key'
            ' assignment.' % self.__class__.__name__
        )

    def __getitem__(self, key):
        """
        Returns a URL to an image sized according to key.

        Arguments:
            * `key`: A string in the following format
                     '[width-in-pixels]x[height-in-pixels]'
                     Example: '400x400'
        """
        try:
            width, height = [int(i) for i in key.split('x')]
        except (KeyError, ValueError):
            raise MalformedSizedImageKey(
                "%s keys must be in the following format: "
                "'`width`x`height`' where both `width` and `height` are "
                "integers." % self.__class__.__name__
            )

        if not self.path_to_image and getattr(
            settings, 'VERSATILEIMAGEFIELD_USE_PLACEHOLDIT', False
        ):
            resized_url = "http://placehold.it/%dx%d" % (width, height)
            resized_storage_path = resized_url
        else:
            resized_storage_path, resized_url = get_resized_path(
                path_to_image=self.path_to_image,
                width=width,
                height=height,
                filename_key=self.get_filename_key(),
                storage=self.storage
            )
            if self.create_on_demand is True:
                if cache.get(resized_url):
                    # The sized path exists in the cache so the image already
                    # exists. So we `pass` to skip directly to the return
                    # statement
                    pass
                else:
                    if resized_storage_path and not self.storage.exists(
                        resized_storage_path
                    ):
                        self.create_resized_image(
                            path_to_image=self.path_to_image,
                            save_path_on_storage=resized_storage_path,
                            width=width,
                            height=height
                        )
                    # Setting a super-long cache for a resized image (30 Days)
                    cache.set(resized_url, 1, VERSATILEIMAGEFIELD_CACHE_LENGTH)
        return SizedImageInstance(resized_storage_path, resized_url)

    def process_image(self, image, image_format, save_kwargs,
                      width, height):
        """
        Arguments:
            * `image`: a PIL Image instance
            * `image_format`: A valid image mime type (e.g. 'image/jpeg')
            * `save_kwargs`: A dict of any keyword arguments needed during
                             save that are provided by the preprocessing API.
            * `width`: value in pixels (as int) representing the intended width
            * `height`: value in pixels (as int) representing the intended
                        height


        Returns a BytesIO representation of the resized image.

        Subclasses MUST implement this method.
        """
        raise NotImplementedError(
            'Subclasses MUST provide a `process_image` method.')

    def preprocess_GIF(self, image, **kwargs):
        """
        Receives a PIL Image instance of a GIF and returns 2-tuple:
            * [0]: Original Image instance (passed to `image`)
            * [1]: Dict with a transparency key (to GIF transparency layer)
        """
        if 'transparency' in image.info:
            save_kwargs = {'transparency': image.info['transparency']}
        else:
            save_kwargs = {}
        return (image, save_kwargs)

    def preprocess_JPEG(self, image, **kwargs):
        """
        Receives a PIL Image instance of a JPEG and returns 2-tuple:
            * [0]: Image instance, converted to RGB
            * [1]: Dict with a quality key (mapped to the value of `QUAL` as
                   defined by the `VERSATILEIMAGEFIELD_JPEG_RESIZE_QUALITY`
                   setting)
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return (image, {'quality': QUAL})

    def create_resized_image(self, path_to_image, save_path_on_storage,
                             width, height):
        """
        Creates a resized image.
        `path_to_image`: The path to the image with the media directory to
                         resize. If `None`, the
                         VERSATILEIMAGEFIELD_PLACEHOLDER_IMAGE will be used.
        `save_path_on_storage`: Where on self.storage to save the resized image
        `width`: Width of resized image (int)
        `height`: Desired height of resized image (int)
        `filename_key`: A string that will be used in the sized image filename
                        to signify what operation was done to it.
                        Examples: 'crop' or 'scale'
        """
        image, file_ext, image_format, mime_type = self.retrieve_image(
            path_to_image
        )

        image, save_kwargs = self.preprocess(image, image_format)

        imagefile = self.process_image(
            image=image,
            image_format=image_format,
            save_kwargs=save_kwargs,
            width=width,
            height=height
        )
        self.save_image(imagefile, save_path_on_storage, file_ext, mime_type)
