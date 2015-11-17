from django.forms import ModelForm

from versatileimagefield.fields import SizedImageCenterpointClickDjangoAdminField

from .models import VersatileImageTestModel, VersatileImageWidgetTestModel


class VersatileImageTestModelForm(ModelForm):
    """
    A form for testing VersatileImageFields
    """
    image = SizedImageCenterpointClickDjangoAdminField()

    class Meta:
        model = VersatileImageTestModel
        fields = (
            'img_type',
            'image',
            'optional_image'
        )


class VersatileImageTestModelFormDjango15(VersatileImageTestModelForm):
    image = SizedImageCenterpointClickDjangoAdminField(required=False)


class VersatileImageWidgetTestModelForm(ModelForm):
    """
    A form for testing VersatileImageField widgets
    """

    class Meta:
        model = VersatileImageWidgetTestModel
        fields = (
            'optional_image_with_ppoi',
        )
