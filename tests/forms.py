from django.forms import ModelForm, ImageField

from .models import VersatileImageTestModel


class VersatileImageTestModelForm(ModelForm):
    """
    A form for testing VersatileImageFields
    """
    image = ImageField()
    optional_image = ImageField()

    class Meta:
        model = VersatileImageTestModel
        fields = (
            'img_type',
            'image',
            'optional_image'
        )
