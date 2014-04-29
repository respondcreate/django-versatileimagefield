from django.forms.fields import (
    ChoiceField,
    MultiValueField,
    CharField,
    ImageField
)

from .widgets import (
    VersatileImagePPOIClickWidget,
    VersatileImagePPOISelectWidget,
    SizedImageCenterpointClickDjangoAdminWidget,
    CENTERPOINT_CHOICES
)


class VersatileImageForFormImageField(ImageField):
    """
    A django.forms.fields.ImageField subclass that provides
    proper validation when displaying fields.VersatileImageField
    as a HTML form.
    """

    def to_python(self, data):
        """
        Ensures `data` is opened so django.forms.fields.ImageField
        validation runs correctly
        """
        if data:
            data.open()
        return super(VersatileImageForFormImageField, self).to_python(data)


class SizedImageCenterpointMixIn(object):

    def compress(self, data_list):
        return tuple(data_list)


class VersatileImagePPOISelectField(SizedImageCenterpointMixIn,
                                    MultiValueField):
    widget = VersatileImagePPOISelectWidget

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length', None)
        del max_length
        fields = (
            VersatileImageForFormImageField(label='Image'),
            ChoiceField(choices=CENTERPOINT_CHOICES, label='Centerpoint')
        )
        super(VersatileImagePPOISelectField, self).__init__(
            tuple(fields), *args, **kwargs
        )


class VersatileImagePPOIClickField(SizedImageCenterpointMixIn,
                                   MultiValueField):
    widget = VersatileImagePPOIClickWidget

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length', None)
        del max_length
        fields = (
            VersatileImageForFormImageField(label='Image'),
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
