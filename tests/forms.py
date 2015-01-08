from django.forms import ModelForm

from .models import VersatileImageTestModel


class VersatileImageTestModelForm(ModelForm):
    """
    A form for testing VersatileImageFields
    """

    class Meta:
        model = VersatileImageTestModel
        fields = (
            'img_type',
            'image',
            'optional_image'
        )
