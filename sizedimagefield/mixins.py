from django.conf import settings
from django.utils import six

from .registry import autodiscover, sizedimageregistry
from .validators import (
    validate_centerpoint,
    validate_centerpoint_tuple,
    ValidationError
)

# Finding SizedImage subclasses (stored in sizedimage.py files
# within apps on settings.INSTALLED_APPS)
autodiscover()

class SizedImageMixIn(object):
    crop_centerpoint = (0.5, 0.5)

    def __init__(self, *args, **kwargs):
        if kwargs.get('crop_centerpoint', None):
            self.crop_centerpoint = kwargs['crop_centerpoint']
            del kwargs['crop_centerpoint']

        super(SizedImageMixIn, self).__init__(*args, **kwargs)
        for attr_name, sizedimage_cls in sizedimageregistry._sizedimage_registry.iteritems():
            setattr(
                self,
                attr_name,
                sizedimage_cls(
                    path_to_image=self.name,
                    storage=self.storage
                )
            )

    def __setattr__(self, key, value):
        if key == 'crop_centerpoint':
            if not value:
                return self.crop_centerpoint
            else:
                center_point = self.validate_crop_centerpoint(value)
                if center_point is not False:
                    super(SizedImageMixIn, self).__setattr__(key, center_point)
        else:
            super(SizedImageMixIn, self).__setattr__(key, value)

    def validate_crop_centerpoint(self, val):
        valid = True
        while valid == True:
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
                message="%s is in invalid centerpoint. `crop_centerpoint` must provide two coordinates, one for the x axis and one for the y where both values are between 0 and 1. You may pass it as either a two-position tuple like this: (0.5,0.5) or as a string where the two values are separated by an 'x' like this: '0.5x0.5'." % val,
                code='invalid_centerpoint'
            )
        else:
            return False
