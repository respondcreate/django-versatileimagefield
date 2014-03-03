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
    """

    """
    name = None
    url = None

    def __init__(self, path_to_image, storage, filename_key):
        super(FilteredImage, self).__init__(path_to_image, storage)
        self.name = get_filtered_path(
            path_to_image=self.path_to_image,
            filename_key=filename_key
        )
        self.url = self.storage.url(self.name)

    def process_filter(self, image, image_format, save_kwargs={}):
        raise NotImplementedError(
            'Subclasses MUST provide a `process_filter` method.')

    def create_filtered_image(self, path_to_image, prepared_path):
        """
        Creates a resized image.
        `path_to_image`: The path to the image with the media directory to
                         resize.
        `prepared_path`: The path on disk to save the filtered image
        """

        image, file_ext, image_format, mime_type = self.retrieve_image(
            path_to_image
        )
        image, save_kwargs = self.preprocess(image, image_format)
        imagefile = self.process_filter(image, image_format, save_kwargs)
        self.save_image(imagefile, prepared_path, file_ext, mime_type)


class DummyFilter(object):
    """
    A 'dummy' version of FilteredImage which is only used if
    .settings.USE_PLACEHOLDIT is True (i.e. if
        django.conf.settings.SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE is unset)
    """
    name = ''
    url = ''


class FilterLibrary(dict):
    """
    Exposes all filters registered with the sizedimageregistry
    (via sizedimageregistry.register_filter) to each SizedImageField.

    Each filter also has access to each 'sizer' registered with
    sizedimageregistry (via sizedimageregistry.register_sizer)
    """

    def __init__(self, original_file_location, storage, registry):
        self.original_file_location = original_file_location
        self.storage = storage
        self.registry = registry

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        """
        Returns a FilteredImage instance built from the FilteredImage subclass
        associated with self.registry[key]

        It no FilteredImage subclass is associated with self.registry[key],
        InvalidFilter raise.
        """
        try:
            # FilteredImage instances are not built until they're accessed for
            # the first time (in order to cut down on memory usage and disk
            # space) However, once built, they can be accessed directly by
            # calling the dict superclass's __getitem__ (which avoids the
            # infinite loop that would be caused by using self[key]
            # or self.get(key))
            prepped_filter = dict.__getitem__(self, key)
        except KeyError:
            # See if `key` is associated with a valid filter.
            if key not in self.registry._filter_registry:
                raise InvalidFilter('`%s` is an invalid filter.' % key)
            else:
                # Handling 'empty' fields.
                if not self.original_file_location and USE_PLACEHOLDIT:
                    # If USE_PLACEHOLDIT is True (i.e.
                    # settings.SIZEDIMAGEFIELD_PLACEHOLDER_IMAGE is unset)
                    # use DummyFilter (so sized renditions can still return
                    # valid http://placehold.it URLs).
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
                        # The filtered_path exists in the cache so the image
                        # already exists. So we `pass` to skip directly to the
                        # return statement.
                        pass
                    else:
                        if not self.storage.exists(filtered_path):
                            prepped_filter.create_filtered_image(
                                path_to_image=self.original_file_location,
                                prepared_path=filtered_path
                            )

                        # Setting a super-long cache for a resized image
                        cache.set(
                            filtered_path,
                            1,
                            SIZEDIMAGEFIELD_CACHE_LENGTH
                        )

                # 'Bolting' all image sizers within
                # `self.registry._sizedimage_registry` onto
                # he prepped_filter instance
                for (
                        attr_name, sizedimage_cls
                ) in self.registry._sizedimage_registry.iteritems():
                    setattr(
                        prepped_filter,
                        attr_name,
                        sizedimage_cls(
                            path_to_image=filtered_path,
                            storage=self.storage
                        )
                    )
                # Assigning `prepped_filter` to `key` so future access
                # is fast/cheap
                self[key] = prepped_filter

        return dict.__getitem__(self, key)
