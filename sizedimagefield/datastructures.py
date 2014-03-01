import os, errno, StringIO

from PIL import Image
import numpy

from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile

from .settings import (
    QUAL,
    USE_PLACEHOLDIT,
    cache,
    SIZEDIMAGEFIELD_CACHE_LENGTH,
    SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE
)
from .utils import (
    get_filtered_path,
    get_resized_path,
    get_image_format_from_file_extension
)

if not USE_PLACEHOLDIT:
    SIZEDIMAGEFIELD_PLACEHOLDER_FOLDER,
    SIZEDIMAGEFIELD_PLACEHOLDER_FILENAME = os.path.split(SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE)

class ProcessedImage(object):

    def __init__(self, path_to_image, storage):
        self.path_to_image = path_to_image
        self.storage = storage

    def process_image(self, image, image_format, **kwargs):
        """
        Arguments:
            * `image`: a PIL Image instance
            * `width`: an int representing the intended width
            * `height`: an int representing the intended height
            * `image_format`: A valid image mime type (e.g. 'image/jpeg')

        Returns a StringIO.StringIO representation of the resized image.

        Subclasses MUST implement this method.
        """
        raise NotImplementedError('Subclasses MUST provide a `process_image` method.')

    def preprocess(self, image, image_format):
        save_kwargs = {'format':image_format}
        if hasattr(self, 'preprocess_%s' % image_format):
            image, addl_save_kwargs = getattr(self, 'preprocess_%s' % image_format)(
                image=image
            )
            save_kwargs.update(addl_save_kwargs)

        return image, save_kwargs


    def retrieve_image(self, path_to_image, prepared_path):
        if not path_to_image:
            containing_folder, filename = os.path.split(prepared_path)
            if not os.path.exists(containing_folder):
                try:
                    os.makedirs(containing_folder)
                except OSError as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir(path):
                        pass
                    else:
                        raise Exception("Can't create directory: '%s' - This is probably due to a permissions issue." % (containing_folder))
            image = SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE
        else:
            image = self.storage.open(path_to_image, 'r')
        file_ext = prepared_path.rsplit('.')[-1]
        image_format, mime_type = get_image_format_from_file_extension(file_ext)

        return (
            Image.open(image),
            file_ext,
            image_format,
            mime_type
        )

    def save_image(self, imagefile, save_path, file_ext, mime_type):
        image_in_memory = Image.open(
            StringIO.StringIO(
                imagefile.getvalue()
            )
        )

        file_to_save = InMemoryUploadedFile(
                            imagefile,
                            None,
                            'foo.%s' % file_ext,
                            mime_type,
                            imagefile.len,
                            None
                        )
        file_to_save.seek(0)
        self.storage.save(save_path, file_to_save)

        return True

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

        image, file_ext, image_format, mime_type = self.retrieve_image(path_to_image, resized_image_path)

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

class FilteredImage(ProcessedImage):
    name = None
    url = None

    def __init__(self, path_to_image, storage, filename_key):
        super(FilteredImage, self).__init__(path_to_image, storage)
        self.name = get_filtered_path(
            path_to_image=self.path_to_image,
            filename_key=filename_key
        )
        self.url = self.storage.url(self.name)

    def add_sizedimage_attrs(self, sizedimage_registry):
        for attr_name, sizedimage_cls in sizedimage_registry.iteritems():
            setattr(
                self,
                attr_name,
                sizedimage_cls(
                    path_to_image=self.name,
                    storage=self.storage
                )
            )

    def process_filter(self, image, image_format, save_kwargs={}):
        raise NotImplementedError('Subclasses MUST provide a `process_filter` method.')

    def create_filtered_image(self, path_to_image, prepared_path):
        """
        Creates a resized image.
        `path_to_image`: The path to the image with the media directory to resize.
        `prepared_path`:
        """

        image, file_ext, image_format, mime_type = self.retrieve_image(path_to_image, prepared_path)
        #print image.__class__
        image, save_kwargs = self.preprocess(image, image_format)
        imagefile = self.process_filter(image, image_format, save_kwargs)
        saved = self.save_image(imagefile, prepared_path, file_ext, mime_type)

        return saved

class Filters(dict):

    def __init__(self, sizedimagefield, registry):
        self.sizedimagefield = sizedimagefield
        self.registry = registry

    def __getitem__(self, key):
        try:
            prepped_filter = dict.__getitem__(self, key)
        except KeyError:
            if key not in self.registry._filter_registry:
                return None
            else:
                filtered_path = get_filtered_path(
                    path_to_image=self.sizedimagefield.name,
                    filename_key=key
                )
                filter_cls = self.registry._filter_registry[key]
                prepped_filter = filter_cls(
                    path_to_image=self.sizedimagefield.name,
                    storage=self.sizedimagefield.storage,
                    filename_key=key
                )
                if cache.get(filtered_path):
                    # The sized path exists in the cache so the image already exists.
                    # So we `pass` to skip directly to the return statement.
                    pass
                else:
                    if not self.sizedimagefield.storage.exists(filtered_path):
                        image_created = prepped_filter.create_filtered_image(
                            path_to_image=self.sizedimagefield.name,
                            prepared_path=filtered_path
                        )

                        # Setting a super-long cache for a resized image (30 Days)
                        cache.set(self.sizedimagefield.name, 1, SIZEDIMAGEFIELD_CACHE_LENGTH)
                for attr_name, sizedimage_cls in self.registry._sizedimage_registry.iteritems():
                    setattr(
                        prepped_filter,
                        attr_name,
                        sizedimage_cls(
                            path_to_image=filtered_path,
                            storage=self.sizedimagefield.storage
                        )
                    )
                self[key] = prepped_filter

        return dict.__getitem__(self, key)
