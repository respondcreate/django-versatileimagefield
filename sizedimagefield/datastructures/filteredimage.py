from ..settings import (
    USE_PLACEHOLDIT,
    cache,
    SIZEDIMAGEFIELD_CACHE_LENGTH
)
from ..utils import get_filtered_path

from .base import ProcessedImage

class InvalidFilter(Exception):
    pass

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

        image, file_ext, image_format, mime_type = self.retrieve_image(path_to_image)
        #print image.__class__
        image, save_kwargs = self.preprocess(image, image_format)
        imagefile = self.process_filter(image, image_format, save_kwargs)
        saved = self.save_image(imagefile, prepared_path, file_ext, mime_type)

        return saved

class DummyFilter(object):
    name = ''
    url = ''

class FilterLibrary(dict):

    def __init__(self, original_file_location, storage, registry):
        self.original_file_location = original_file_location
        self.storage = storage
        self.registry = registry

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        try:
            prepped_filter = dict.__getitem__(self, key)
        except KeyError:
            if key not in self.registry._filter_registry:
                raise InvalidFilter('`%s` is an invalid filter.' % key)
            else:
                if not self.original_file_location and USE_PLACEHOLDIT:
                    filtered_path = None
                    prepped_filter = DummyFilter()
                else:
                    filtered_path = get_filtered_path(
                        path_to_image=self.original_file_location,
                        filename_key=key
                    )
                    filter_cls = self.registry._filter_registry[key]
                    prepped_filter = filter_cls(
                        path_to_image=self.original_file_location,
                        storage=self.storage,
                        filename_key=key
                    )
                    if cache.get(filtered_path):
                        # The sized path exists in the cache so the image already exists.
                        # So we `pass` to skip directly to the return statement.
                        pass
                    else:
                        if not self.storage.exists(filtered_path):
                            image_created = prepped_filter.create_filtered_image(
                                path_to_image=self.original_file_location,
                                prepared_path=filtered_path
                            )

                        # Setting a super-long cache for a resized image (30 Days)
                        cache.set(filtered_path, 1, SIZEDIMAGEFIELD_CACHE_LENGTH)

                for attr_name, sizedimage_cls in self.registry._sizedimage_registry.iteritems():
                    setattr(
                        prepped_filter,
                        attr_name,
                        sizedimage_cls(
                            path_to_image=filtered_path,
                            storage=self.storage
                        )
                    )
                self[key] = prepped_filter

        return dict.__getitem__(self, key)
