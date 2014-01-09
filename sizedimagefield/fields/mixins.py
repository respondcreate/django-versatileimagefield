from django.conf import settings
from django.utils import six

from ..datastructures import (
    CroppedImage,
    ScaledImage
)
from ..utils import validate_centerpoint_tuple
from .exceptions import InvalidCropCenterPoint

class SizedImageMixIn(object):
    crop_center_point = (0.5, 0.5)

    def __init__(self, *args, **kwargs):
        if kwargs.get('crop_center_point', None):
            self.crop_center_point = kwargs['crop_center_point']
            del kwargs['crop_center_point']
        super(SizedImageMixIn, self).__init__(*args, **kwargs)

    def __setattr__(self, key, value):
        if key == 'crop_center_point':
            if not value:
                pass
            else:
                center_point = self.validate_crop_center_point(value)
                if center_point is not False:
                    super(SizedImageMixIn, self).__setattr__(key, center_point)
        else:
            super(SizedImageMixIn, self).__setattr__(key, value)
        return self.crop_center_point

    def validate_crop_center_point(self, val):
        valid = True
        if isinstance(val, tuple):
            to_validate = val
        elif isinstance(val, six.string_types):
            try:
                ccp_split = [float(segment) for segment in val.split('x')]
            except ValueError:
                ccp_split = tuple()
            to_validate = tuple(ccp_split)
        else:
            to_validate = tuple()

        valid = validate_centerpoint_tuple(to_validate)

        if valid:
            return to_validate
        else:
            if getattr(settings, 'DEBUG', True):
                raise InvalidCropCenterPoint("%s is in invalid crop center point. `crop_center_point` must provide two coordinates, one for the x axis and one for the y where both values are between 0 and 1. You may pass it as either a two-position tuple like this: (0.5,0.5) or as a string where the two values are separated by an 'x' like this: '0.5x0.5'." % val)
            else:
                return False

    @property
    def scale(self):
        return ScaledImage(
            path_to_image=self.name,
            storage=self.storage
        )

    @property
    def crop(self):
        return CroppedImage(
            path_to_image=self.name,
            storage=self.storage,
            crop_center_point=self.crop_center_point
        )
