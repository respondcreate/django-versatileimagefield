from django.conf import settings
from django.utils import six

from .datastructures import FilterLibrary
from .registry import autodiscover, sizedimagefield_registry
from .validators import (
    validate_centerpoint,
    validate_centerpoint_tuple,
    ValidationError
)

# Finding SizedImage subclasses (stored in sizedimage.py files
# within apps on settings.INSTALLED_APPS)
autodiscover()


class SizedImageMixIn(object):
    """
    A mix-in that provides the filtering/sizing API and crop centering
    support for django.db.models.fields.files.ImageField
    """

    def __init__(self, *args, **kwargs):
        super(SizedImageMixIn, self).__init__(*args, **kwargs)
        # Setting initial centerpoint
        if self.field.centerpoint_field:
            instance_centerpoint_value = getattr(
                self.instance,
                self.field.centerpoint_field,
                (0.5, 0.5)
            )
            self.crop_centerpoint = instance_centerpoint_value
        else:
            self.crop_centerpoint = (0.5, 0.5)

    @property
    def crop_centerpoint(self):
        return self._centerpoint_value

    @crop_centerpoint.setter
    def crop_centerpoint(self, value):
        centerpoint = self.validate_crop_centerpoint(value)
        if centerpoint is not False:
            self._centerpoint_value = centerpoint
            self.build_filters_and_sizers(centerpoint)

    def build_filters_and_sizers(self, centerpoint_value):
        self.filters = FilterLibrary(
            self.name,
            self.storage,
            sizedimagefield_registry,
            centerpoint_value
        )
        for (
            attr_name,
            sizedimage_cls
        ) in sizedimagefield_registry._sizedimage_registry.iteritems():
            setattr(
                self,
                attr_name,
                sizedimage_cls(
                    path_to_image=self.name,
                    storage=self.storage,
                    crop_centerpoint=centerpoint_value
                )
            )

    def validate_crop_centerpoint(self, val):
        valid = True
        while valid is True:
            to_validate = None
            if isinstance(val, tuple):
                to_validate = val
            elif isinstance(val, six.string_types):
                try:
                    to_validate = validate_centerpoint(
                        val,
                        return_converted_tuple=True
                    )
                except ValidationError:
                    valid = False
            else:
                valid = False

            if to_validate and validate_centerpoint_tuple(to_validate):
                return to_validate
            break

        if getattr(settings, 'DEBUG', True):
            raise ValidationError(
                message="`%s` is in invalid centerpoint. `crop_centerpoint` "
                        "must provide two coordinates, one for the x axis and "
                        "one for the y where both values are between 0 and 1. "
                        "You may pass it as either a two-position tuple like "
                        "this: (0.5, 0.5) or as a string where the two values"
                        "are separated by an 'x' like this: '0.5x0.5'." % str(
                            val
                        ),
                code='invalid_centerpoint'
            )
        else:
            return False
