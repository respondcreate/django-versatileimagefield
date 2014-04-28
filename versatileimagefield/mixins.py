from django.conf import settings
from django.utils import six

from .datastructures import FilterLibrary
from .registry import autodiscover, versatileimagefield_registry
from .validators import (
    validate_ppoi,
    validate_ppoi_tuple,
    ValidationError
)

# Finding SizedImage subclasses (stored in sizedimage.py files
# within apps on settings.INSTALLED_APPS)
autodiscover()


class VersatileImageMixIn(object):
    """
    A mix-in that provides the filtering/sizing API and crop centering
    support for django.db.models.fields.files.ImageField
    """

    def __init__(self, *args, **kwargs):
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
    def ppoi(self):
        return self._ppoi_value

    @ppoi.setter
    def ppoi(self, value):
        ppoi = self.validate_ppoi(value)
        if ppoi is not False:
            self._ppoi_value = ppoi
            self.build_filters_and_sizers(ppoi)

    def build_filters_and_sizers(self, ppoi_value):
        self.filters = FilterLibrary(
            self.name,
            self.storage,
            versatileimagefield_registry,
            ppoi_value
        )
        for (
            attr_name,
            sizedimage_cls
        ) in versatileimagefield_registry._sizedimage_registry.iteritems():
            setattr(
                self,
                attr_name,
                sizedimage_cls(
                    path_to_image=self.name,
                    storage=self.storage,
                    ppoi=ppoi_value
                )
            )

    def validate_ppoi(self, val):
        valid = True
        while valid is True:
            to_validate = None
            if isinstance(val, tuple):
                to_validate = val
            elif isinstance(val, six.string_types):
                try:
                    to_validate = validate_ppoi(
                        val,
                        return_converted_tuple=True
                    )
                except ValidationError:
                    valid = False
            else:
                valid = False

            if to_validate and validate_ppoi_tuple(to_validate):
                return to_validate
            break

        if getattr(settings, 'DEBUG', True):
            raise ValidationError(
                message="`%s` is in invalid ppoi. `ppoi` "
                        "must provide two coordinates, one for the x axis and "
                        "one for the y where both values are between 0 and 1. "
                        "You may pass it as either a two-position tuple like "
                        "this: (0.5, 0.5) or as a string where the two values"
                        "are separated by an 'x' like this: '0.5x0.5'." % str(
                            val
                        ),
                code='invalid_ppoi'
            )
        else:
            return False
