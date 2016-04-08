from __future__ import unicode_literals

import os
import re

from django.utils.six import iteritems

from .datastructures import FilterLibrary
from .registry import autodiscover, versatileimagefield_registry
from .settings import (
    cache,
    VERSATILEIMAGEFIELD_CREATE_ON_DEMAND,
    VERSATILEIMAGEFIELD_SIZED_DIRNAME,
    VERSATILEIMAGEFIELD_FILTERED_DIRNAME
)
from .validators import validate_ppoi

autodiscover()

filter_regex_snippet = r'__({registered_filters})__'.format(
    registered_filters='|'.join([
        key
        for key, filter_cls in iteritems(
            versatileimagefield_registry._filter_registry
        )
    ])
)
sizer_regex_snippet = r'-({registered_sizers})-(\d+)x(\d+)(?:-\d+)?'.format(
    registered_sizers='|'.join([
        key
        for key, filter_cls in iteritems(
            versatileimagefield_registry._sizedimage_registry
        )
    ])
)


class VersatileImageMixIn(object):
    """
    A mix-in that provides the filtering/sizing API and crop centering
    support for django.db.models.fields.files.ImageField
    """

    def __init__(self, *args, **kwargs):
        self._create_on_demand = VERSATILEIMAGEFIELD_CREATE_ON_DEMAND
        super(VersatileImageMixIn, self).__init__(*args, **kwargs)
        # Setting initial ppoi
        if self.field.ppoi_field:
            instance_ppoi_value = getattr(
                self.instance,
                self.field.ppoi_field,
                (0.5, 0.5)
            )
            self.ppoi = instance_ppoi_value
        else:
            self.ppoi = (0.5, 0.5)
        if self.name:
            filename, ext = os.path.splitext(self.name)
            self.filter_regex = re.compile(
                "{filename}{filter_regex_snippet}{ext}".format(
                    filename=filename,
                    filter_regex_snippet=filter_regex_snippet,
                    ext=ext
                )
            )
            self.sizer_regex = re.compile(
                "{filename}{sizer_regex_snippet}{ext}".format(
                    filename=filename,
                    sizer_regex_snippet=sizer_regex_snippet,
                    ext=ext
                )
            )
            self.filter_and_sizer_regex = re.compile(
                "{filename}{filter_regex_snippet}"
                "{sizer_regex_snippet}.{ext}".format(
                    filename=filename,
                    filter_regex_snippet=filter_regex_snippet,
                    sizer_regex_snippet=sizer_regex_snippet,
                    ext=ext
                )
            )

    def _get_url(self):
        """
        Returns the appropriate URL based on field conditions:
            * If empty (not `self.name`) and a placeholder is defined, the
              URL to the placeholder is returned.
            * Otherwise, defaults to vanilla ImageFieldFile behavior.
        """
        if not self.name and self.field.placeholder_image_name:
            return self.storage.url(self.field.placeholder_image_name)
        return super(VersatileImageMixIn, self)._get_url()
    url = property(_get_url)

    @property
    def create_on_demand(self):
        return self._create_on_demand

    @create_on_demand.setter
    def create_on_demand(self, value):
        if not isinstance(value, bool):
            raise ValueError(
                "`create_on_demand` must be a boolean"
            )
        else:
            self._create_on_demand = value
            self.build_filters_and_sizers(self.ppoi, value)

    @property
    def ppoi(self):
        return self._ppoi_value

    @ppoi.setter
    def ppoi(self, value):
        ppoi = validate_ppoi(
            value,
            return_converted_tuple=True
        )
        if ppoi is not False:
            self._ppoi_value = ppoi
            self.build_filters_and_sizers(ppoi, self.create_on_demand)

    def build_filters_and_sizers(self, ppoi_value, create_on_demand):
        name = self.name
        if not name and self.field.placeholder_image_name:
            name = self.field.placeholder_image_name
        self.filters = FilterLibrary(
            name,
            self.storage,
            versatileimagefield_registry,
            ppoi_value,
            create_on_demand
        )
        for (
            attr_name,
            sizedimage_cls
        ) in iteritems(versatileimagefield_registry._sizedimage_registry):
            setattr(
                self,
                attr_name,
                sizedimage_cls(
                    path_to_image=name,
                    storage=self.storage,
                    create_on_demand=create_on_demand,
                    ppoi=ppoi_value
                )
            )

    def get_filtered_root_folder(self):
        """
        Returns the folder on `self.storage` where filtered images created
        from `self.name` are stored.
        """
        folder, filename = os.path.split(self.name)
        return os.path.join(folder, VERSATILEIMAGEFIELD_FILTERED_DIRNAME, '')

    def get_sized_root_folder(self):
        """
        Returns the folder on `self.storage` where sized images created
        from `self.name` are stored.
        """
        folder, filename = os.path.split(self.name)
        return os.path.join(VERSATILEIMAGEFIELD_SIZED_DIRNAME, folder, '')

    def get_filtered_sized_root_folder(self):
        """
        Returns the folder on `self.storage` where filtered sized images
        created from `self.name` are stored.
        """
        sized_root_folder = self.get_sized_root_folder()
        return os.path.join(
            sized_root_folder,
            VERSATILEIMAGEFIELD_FILTERED_DIRNAME
        )

    def delete_matching_files_from_storage(self, root_folder, regex):
        """
        Deletes files from `root_folder` on self.storage that match
        `regex`.
        """
        directory_list, file_list = self.storage.listdir(root_folder)
        for f in file_list:
            if regex.match(f) is not None:
                file_location = os.path.join(root_folder, f)
                self.storage.delete(file_location)
                cache.delete(
                    self.storage.url(file_location)
                )
                print(
                    "Deleted {file} (created from: {original})".format(
                        file=os.path.join(root_folder, f),
                        original=self.name
                    )
                )

    def delete_filtered_images(self):
        """
        Deletes all filtered images created from `self.name`.
        """
        self.delete_matching_files_from_storage(
            self.get_filtered_root_folder(),
            self.filter_regex
        )

    def delete_sized_images(self):
        """
        Deletes all sized images created from `self.name`.
        """
        self.delete_matching_files_from_storage(
            self.get_sized_root_folder(),
            self.sizer_regex
        )

    def delete_filtered_sized_images(self):
        """
        Deletes all filtered sized images created from `self.name`.
        """
        self.delete_matching_files_from_storage(
            self.get_filtered_sized_root_folder(),
            self.filter_and_sizer_regex
        )

    def delete_all_created_images(self):
        """
        Deletes all images created from `self.name`.
        """
        self.delete_filtered_images()
        self.delete_sized_images()
        self.delete_filtered_sized_images()
