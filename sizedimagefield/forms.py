from django.forms.fields import ChoiceField, FileField, MultiValueField, CharField

from .widgets import (
    SizedImageCenterpointClickWidget,
    SizedImageCenterpointSelectWidget,
    CENTERPOINT_CHOICES
)

class SizedImageCenterpointMixIn(object):

    def compress(self, data_list):
        return tuple(data_list)


class SizedImageCenterpointSelectField(SizedImageCenterpointMixIn, MultiValueField):
    widget = SizedImageCenterpointSelectWidget

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length', None)
        fields = (
            FileField(label='File'),
            ChoiceField(choices=CENTERPOINT_CHOICES, label='Centerpoint')
        )
        super(SizedImageCenterpointSelectField, self).__init__(tuple(fields), *args, **kwargs)

class SizedImageCenterpointClickField(SizedImageCenterpointMixIn, MultiValueField):
    widget = SizedImageCenterpointClickWidget

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length', None)
        fields = (
            FileField(label='File'),
            CharField()
        )
        super(SizedImageCenterpointClickField, self).__init__(tuple(fields), *args, **kwargs)
