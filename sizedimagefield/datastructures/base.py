import os, StringIO

from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile

from ..settings import (
    USE_PLACEHOLDIT,
    SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE
)
from ..utils import  get_image_metadata_from_file_ext

if not USE_PLACEHOLDIT:
    PLACEHOLDER_FOLDER, PLACEHOLDER_FILENAME = os.path.split(SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE)

class ProcessedImage(object):

    def __init__(self, path_to_image, storage):
        self.path_to_image = path_to_image
        self.storage = storage

    def process_image(self, image, image_format, **kwargs):
        """
        Arguments:
            * `image`: a PIL Image instance
            * `image_format`: str, a valid PIL format (i.e. 'JPEG' or 'GIF')

        Returns a StringIO.StringIO representation of the resized image.

        Subclasses MUST implement this method.
        """
        raise NotImplementedError('Subclasses MUST provide a `process_image` method.')

    def preprocess(self, image, image_format):
        """
        An API hook for image pre-processing. Calls any image format specific
        pre-processors (if defined). I.E. If `image_format` is 'JPEG', this method
        will look for a method named `preprocess_JPEG`, if found `image` will be
        passed to it.

        Arguments:
            * `image`: a PIL Image instance
            * `image_format`: str, a valid PIL format (i.e. 'JPEG' or 'GIF')
        """
        save_kwargs = {'format':image_format}
        if hasattr(self, 'preprocess_%s' % image_format):
            image, addl_save_kwargs = getattr(self, 'preprocess_%s' % image_format)(
                image=image
            )
            save_kwargs.update(addl_save_kwargs)

        return image, save_kwargs


    def retrieve_image(self, path_to_image):
        """
        Returns a PIL Image instance stored at `path_to_image`

        If `path_to_image` is None, the global Placeholder image (as specified
        by the SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE setting) will be returned.
        """
        if not path_to_image:
            image = SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE
            file_ext = image.rsplit('.')[-1]
        else:
            image = self.storage.open(path_to_image, 'r')
            file_ext = path_to_image.rsplit('.')[-1]
        image_format, mime_type = get_image_metadata_from_file_ext(file_ext)

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
