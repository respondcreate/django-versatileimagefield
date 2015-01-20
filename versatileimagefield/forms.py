from __future__ import unicode_literals

from django.forms.fields import (
    MultiValueField,
    CharField,
    ImageField
)

from .widgets import (
    VersatileImagePPOIClickWidget,
    SizedImageCenterpointClickDjangoAdminWidget
)


class SizedImageCenterpointMixIn(object):

    def compress(self, data_list):
        return tuple(data_list)


class VersatileImagePPOIClickField(SizedImageCenterpointMixIn,
                                   MultiValueField):
    widget = VersatileImagePPOIClickWidget

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length', None)
        del max_length
        fields = (
            ImageField(label='Image'),
            CharField(required=False)
        )
        super(VersatileImagePPOIClickField, self).__init__(
            tuple(fields), *args, **kwargs
        )


class SizedImageCenterpointClickDjangoAdminField(
        VersatileImagePPOIClickField):
    widget = SizedImageCenterpointClickDjangoAdminWidget
    # Need to remove `None` and `u''` so required fields will work
    # TODO: Better validation handling
    empty_values = [[], (), {}]
