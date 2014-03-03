import os

from PIL import Image
import numpy

from ..settings import (
    QUAL,
    USE_PLACEHOLDIT,
    cache,
    SIZEDIMAGEFIELD_CACHE_LENGTH,
    SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE
)
from ..utils import get_resized_path
from .base import ProcessedImage

class SizedImage(ProcessedImage, dict):

    def __init__(self, path_to_image, storage):

        if getattr(self, 'filename_key', None) is None:
            raise NotImplementedError(
                "%s instances MUST have a `filename_key` attribute" % self.__class__.__name__
            )
        super(SizedImage, self).__init__(path_to_image, storage)

    def get_filename_key(self):
        """
        Returns a string that will be used to identify the resized image.
        """
        if not getattr(self, 'filename_key'):
            raise AttributError('SizedImage subclasses must define a `filename_key` '
                                'attribute or override the `get_filename_key` method.')
        else:
            return self.filename_key

    def __setitem__(self, key, value):
        raise NotImplementedError(
            '%s instances do not allow key assignment.' % self.__class__.__name__
        )

    def __getitem__(self, key):
        """"""
        try:
            width, height = [int(i) for i in key.split('x')]
        except KeyError:
            raise SizedImageDictKeyError(
                "%s keys must be in the following format: "
                "'`width`x`height`' where both `width` and `height` are "
                "integers." % self.__class__.__name__
            )

        if not self.path_to_image and USE_PLACEHOLDIT:
            resized_url = "http://placehold.it/%dx%d" % (width, height)
        else:
            resized_url = get_resized_path(
                path_to_image=self.path_to_image,
                width=width,
                height=height,
                filename_key=self.get_filename_key(),
                base_url=self.storage.base_url
            )
            if cache.get(resized_url):
                # The sized path exists in the cache so the image already exists.
                # So we `pass` to skip directly to the return statement.
                pass
            else:
                resized_image_path = get_resized_path(
                    path_to_image=self.path_to_image,
                    width=width,
                    height=height,
                    filename_key=self.get_filename_key()
                )
                if not self.storage.exists(resized_image_path):
                    image_created = self.create_resized_image(
                        path_to_image=self.path_to_image,
                        width=width,
                        height=height,
                        filename_key=self.get_filename_key()
                    )
                # Setting a super-long cache for a resized image (30 Days)
                cache.set(resized_url, 1, SIZEDIMAGEFIELD_CACHE_LENGTH)
        return resized_url

    def process_image(self, image, image_format, width, height, save_kwargs={}):
        """
        Arguments:
            * `image`: a PIL Image instance
            * `width`: value in pixels (as int) representing the intended width
            * `height`: value in pixels (as int) representing the intended height
            * `image_format`: A valid image mime type (e.g. 'image/jpeg')

        Returns a StringIO.StringIO representation of the resized image.

        Subclasses MUST implement this method.
        """
        raise NotImplementedError('Subclasses MUST provide a `process_image` method.')

    def preprocess_PNG(self, image, **kwargs):
        """
        Receives a PIL Image instance of a PNG and returns a 2-tuple:
            * [0]: Image instance with a properly processed alpha (transparency) layer that
                   is resize ready. (Found here: http://stackoverflow.com/a/9146202/1149774)
            * [1]: Empty dict ({})
        """
        premult = numpy.fromstring(image.tobytes(), dtype=numpy.uint8)
        alpha_layer = premult[3::4] / 255.0
        premult[::4] *= alpha_layer
        premult[1::4] *= alpha_layer
        premult[2::4] *= alpha_layer
        return (Image.frombytes("RGBA", image.size, premult.tostring()), {})

    def preprocess_GIF(self, image, **kwargs):
        """
        Receives a PIL Image instance of a GIF and returns 2-tuple:
            * [0]: Original Image instance (passed to `image`)
            * [1]: Dict with a transparency key (to GIF transparency layer)
        """
        return (image, {'transparency': image.info['transparency']})

    def preprocess_JPEG(self, image, **kwargs):
        """
        Receives a PIL Image instance of a JPEG and returns 2-tuple:
            * [0]: Image instance, converted to RGB
            * [1]: Dict with a quality key (mapped to the value of `QUAL` as
                   defined by the `SIZEDIMAGEFIELD_JPEG_RESIZE_QUALITY` setting)
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return (image, {'quality': QUAL})

    def create_resized_image(self, path_to_image, width, height, filename_key):
        """
        Creates a resized image.
        `path_to_image`: The path to the image with the media directory to resize.
            If `None`, the SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE will be used.
        `width`: Width of resized image (int)
        `height`: Desired height of resized image (int)
        `filename_key`: A string that will be used in the sized image filename to signify
        what operation was done to it. Examples: 'crop' or 'scale'
        """
        resized_image_path = get_resized_path(
            path_to_image=path_to_image,
            width=width,
            height=height,
            filename_key=filename_key
        )

        image, file_ext, image_format, mime_type = self.retrieve_image(path_to_image)

        image, save_kwargs = self.preprocess(image, image_format)

        imagefile = self.process_image(
            image=image,
            image_format=image_format,
            width=width,
            height=height,
            save_kwargs=save_kwargs
        )

        saved = self.save_image(imagefile, resized_image_path, file_ext, mime_type)

        return saved
