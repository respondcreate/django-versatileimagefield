from django.conf import settings
from django.utils import six

from ..datastructures import (
    CroppedImage,
    ScaledImage
)
from ..utils import (
    convert_string_to_centerpoint_tuple,
    validate_centerpoint_tuple,
    InvalidCropCenterPoint
)

class SizedImageMixIn(object):
    crop_centerpoint = (0.5, 0.5)

    def __init__(self, *args, **kwargs):
        if kwargs.get('crop_centerpoint', None):
            self.crop_centerpoint = kwargs['crop_centerpoint']
            del kwargs['crop_centerpoint']
        super(SizedImageMixIn, self).__init__(*args, **kwargs)

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
        if isinstance(val, tuple):
            to_validate = val
        elif isinstance(val, six.string_types):
            try:
                to_validate = convert_string_to_centerpoint_tuple(val)
            except InvalidCropCenterPoint:
                valid = False
        else:
            valid = False
        if valid:
            if validate_centerpoint_tuple(to_validate):
                return to_validate
        else:
            if getattr(settings, 'DEBUG', True):
                raise InvalidCropCenterPoint("%s is in invalid centerpoint. `crop_centerpoint` must provide two coordinates, one for the x axis and one for the y where both values are between 0 and 1. You may pass it as either a two-position tuple like this: (0.5,0.5) or as a string where the two values are separated by an 'x' like this: '0.5x0.5'." % val)
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
            crop_centerpoint=self.crop_centerpoint
        )
