from django.forms.widgets import ClearableFileInput, MultiWidget, Select

CENTERPOINT_CHOICES = (
    ('0.0x0.0','Top Left'),
    ('0.0x0.5','Top Center'),
    ('0.0x1.0','Top Right'),
    ('0.5x0.0','Middle Left'),
    ('0.5x0.5','Middle Center'),
    ('0.5x1.0','Middle Right'),
    ('1.0x0.0','Bottom Left'),
    ('1.0x0.5','Bottom Center'),
    ('1.0x1.0','Bottom Right'),
)

class SizedImageCenterpointSelectWidget(MultiWidget):

    def __init__(self, widgets=None, attrs=None):
        widgets = [
            ClearableFileInput(attrs=attrs),
            Select(
                attrs=attrs,
                choices=CENTERPOINT_CHOICES
            )
        ]
        super(SizedImageCenterpointSelectWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, u'x'.join(unicode(num) for num in value.crop_centerpoint)]
        return [None, None]
