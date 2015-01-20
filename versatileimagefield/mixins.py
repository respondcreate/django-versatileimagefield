from __future__ import unicode_literals

from django.utils.six import iteritems

from .datastructures import FilterLibrary
from .registry import autodiscover, versatileimagefield_registry
from .settings import VERSATILEIMAGEFIELD_CREATE_ON_DEMAND
from .validators import validate_ppoi

# Finding SizedImage subclasses (stored in sizedimage.py files
# within apps on settings.INSTALLED_APPS)
autodiscover()


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
