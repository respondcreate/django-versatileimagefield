from django.forms.fields import ChoiceField, FileField, MultiValueField

from .widgets import SizedImageCenterpointSelectWidget, CENTERPOINT_CHOICES

class SizedImageCenterpointSelectField(MultiValueField):
    widget = SizedImageCenterpointSelectWidget

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length')
        fields = (
            FileField(label='File'),
            ChoiceField(choices=CENTERPOINT_CHOICES, label='Centerpoint')
        )
        super(SizedImageCenterpointSelectField, self).__init__(tuple(fields), *args, **kwargs)

    def compress(self, data_list):
        return tuple(data_list)

