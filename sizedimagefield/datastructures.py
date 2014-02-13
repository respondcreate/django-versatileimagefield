import os, errno
import StringIO

from PIL import ImageOps, Image

from django.conf import settings
from django.core.cache import (
    cache as default_cache,
    get_cache,
    InvalidCacheBackendError
)
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile

QUAL = getattr(settings, 'SIZEDIMAGEFIELD_RESIZE_IMAGE_QUALITY', 70)

SIZEDIMAGEFIELD_DIRECTORY_NAME = '__sized'
SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE = getattr(settings, 'SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE', None)

if not SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE:
    USE_PLACEHOLDIT = True
else:
    USE_PLACEHOLDIT = False
    SIZEDIMAGEFIELD_PLACEHOLDER_FOLDER,
    SIZEDIMAGEFIELD_PLACEHOLDER_FILENAME = os.path.split(SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE)

try:
    cache = get_cache('sizedimagefield_cache')
except InvalidCacheBackendError:
    cache = default_cache

SIZEDIMAGEFIELD_CACHE_LENGTH = getattr(settings, 'SIZEDIMAGEFIELD_CACHE_LENGTH', 2592000)

class SizedImage(dict):

    def __init__(self, path_to_image, storage):
        self.path_to_image = path_to_image
        self.storage = storage
        if getattr(self, 'filename_key', None) is None:
            raise NotImplementedError(
                "Subclasses MUST provide a `filename_key` attribute"
            )

    def __setitem__(self, key, value):
        raise NotImplementedError(
            '%s instances do not allow key assignment.' % self.__class__.__name__
        )

    def __getitem__(self, key):
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
            resized_url = self.get_resized_path(
                path_to_image=self.path_to_image,
                width=width,
                height=height,
                filename_key=self.get_filename_key(),
                for_url=True
            )
            if cache.get(resized_url):
                # The sized path exists in the cache so the image already exists.
                # So we `pass` to skip directly to the return statement.
                pass
            else:
                resized_image_path = self.get_resized_path(
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

    def get_filename_key(self):
        return self.filename_key

    @staticmethod
    def get_resized_filename(filename, width, height, filename_key):
        """
        Returns the 'resized filename' (according to `width`, `height` and `filename_key`)
        in the following format:
        `filename`-`filename_key`-`width`x`height`.ext
        """
        try:
            image_name, ext = filename.rsplit('.', 1)
        except ValueError:
            image_name = filename
            ext = 'jpg'
        return "%(image_name)s-%(filename_key)s-%(width)dx%(height)d.%(ext)s" % ({
            'image_name':image_name,
            'filename_key':filename_key,
            'width':width,
            'height':height,
            'ext':ext
        })

    def get_resized_path(self, path_to_image, width, height, filename_key, for_url=False):
        """
        Returns the 'resized' path of `path_to_image`
        """
        if not path_to_image:
            filename = SIZEDIMAGEFIELD_PLACEHOLDER_FILENAME
            containing_folder = 'GLOBAL-PLACEHOLDER'
        else:
            containing_folder, filename = os.path.split(path_to_image)

        resized_filename = self.get_resized_filename(filename, width, height, filename_key)

        joined_path = os.path.join(*[
            SIZEDIMAGEFIELD_DIRECTORY_NAME,
            containing_folder,
            resized_filename
        ])

        if for_url:
            path_to_return = self.storage.url(joined_path)
        else:
            path_to_return = joined_path
        # Removing spaces so this path is memcached key friendly
        return path_to_return.replace(' ', '')

    def process_image(self, image, return_image=False):
        raise NotImplementedError('Subclasses MUST provide a `process_image` method.')

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
        resized_image_path = self.get_resized_path(
            path_to_image=path_to_image,
            width=width,
            height=height,
            filename_key=filename_key
        )
        if not path_to_image:
            containing_folder, filename = os.path.split(resized_image_path)
            if not os.path.exists(containing_folder):
                try:
                    os.makedirs(containing_folder)
                except OSError as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir(path):
                        pass
                    else:
                        raise Exception("Can't create directory: '%s' - This is probably due to a permissions issue." % (containing_folder))
            image_to_resize = SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE
        else:
            image_to_resize = self.storage.open(path_to_image, 'r')

        image = Image.open(image_to_resize)

        imagefile = self.process_image(image, width, height)

        image_in_memory = Image.open(
            StringIO.StringIO(
                imagefile.getvalue()
            )
        )

        file_to_save = InMemoryUploadedFile(
                            imagefile,
                            None,
                            'foo.jpg',
                            'image/jpeg',
                            imagefile.len,
                            None
                        )
        file_to_save.seek(0)
        self.storage.save(resized_image_path, file_to_save)

        return True

class CroppedImage(SizedImage):
    filename_key = 'crop'

    def __init__(self, path_to_image, storage, crop_centerpoint=(0.5, 0.5)):
        self.crop_centerpoint = crop_centerpoint
        super(CroppedImage, self).__init__(path_to_image, storage)

    @property
    def crop_centerpoint_as_str(self):
        return "%s__%s" % (
            str(self.crop_centerpoint[0]).replace('.', '-'),
            str(self.crop_centerpoint[1]).replace('.', '-')
        )

    def get_filename_key(self):
        return "%s-c%s" % (
            self.filename_key,
            self.crop_centerpoint_as_str
        )

    def process_image(self, image, width, height):
        imagefile = StringIO.StringIO()

        if image.mode != 'RGB':
            image = image.convert('RGB')

        ImageOps.fit(
            image=image,
            size=(width, height),
            method=Image.ANTIALIAS,
            centering=self.crop_centerpoint
        ).save(
            imagefile,
            format="jpeg",
            quality=QUAL
        )
        image_in_memory = Image.open(
            StringIO.StringIO(
                imagefile.getvalue()
            )
        )

        return imagefile

class ScaledImage(SizedImage):
    filename_key = 'scale'

    def process_image(self, image, width, height):
        imagefile = StringIO.StringIO()

        if image.mode != 'RGB':
            image = image.convert('RGB')

        image.thumbnail(
            (width, height),
            Image.ANTIALIAS
        )
        # IMPORANT! When creating thumbnails the save method MUST be called separately
        # from the thumbnail method (and not chained in at the end). Why? WHO KNOWS?!
        image.save(
            imagefile,
            format="jpeg",
            quality=QUAL
        )

        return imagefile
