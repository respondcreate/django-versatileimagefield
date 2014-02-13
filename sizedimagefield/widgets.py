from django.forms.widgets import (
    CheckboxInput, ClearableFileInput, FileInput,
    HiddenInput, MultiWidget, Select
)
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

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

class ClearableFileInputWithImagePreview(ClearableFileInput):
    centerpoint_label = ugettext_lazy('Select Centerpoint')
    template_with_clear = '%(clear)s <label class="sizedimagefield-label" for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'
    template_with_initial_and_imagepreview = """
    <div class="sizedimage-mod initial">
        <label class="sizedimagefield-label">%(initial_text)s</label>
        %(initial)s
    </div>
    <div class="sizedimage-mod clear">
        %(clear_template)s
    </div>
    <div class="sizedimage-mod preview">
        <label class="sizedimagefield-label">%(centerpoint_label)s</label>
        %(image_preview)s
    </div>
    <div class="sizedimage-mod new-upload">
        <label class="sizedimagefield-label">%(input_text)s</label>
        %(input)s
    </div>"""

    def image_preview_id(self, name):
        """
        Given the name of the image preview tag, return the HTML id for it.
        """
        return name + '_imagepreview'

    def image_preview(self, image_preview_id, value):
        """
        Given the name of the image preview tag, return the HTML id for it.
        """
        return '<img src="%(sized_url)s" id="%(image_preview_id)s" class="sizedimage-preview"/>' % {
            'sized_url':value.scale['300x100'],
            'image_preview_id':image_preview_id
        }

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': force_text(self.initial_text),
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
            'centerpoint_label':self.centerpoint_label
        }
        template = '%(input)s'
        substitutions['input'] = super(FileInput, self).render(name, value, attrs)
        if value and hasattr(value, "url"):
            substitutions['initial'] = format_html('<a href="{0}">{1}</a>',
                                                   value.url,
                                                   force_text(value))
            if value.field.centerpoint_field:
                template = self.template_with_initial_and_imagepreview
                image_preview_id = self.image_preview_id(name)
                image_preview = self.image_preview(image_preview_id, value)
                substitutions['image_preview'] = image_preview
            else:
                template = self.template_with_initial

            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions
        return mark_safe(template % substitutions)

class SizedImageCenterpointWidgetMixIn(object):

    def decompress(self, value):
        if value:
            return [value, u'x'.join(unicode(num) for num in value.crop_centerpoint)]
        return [None, None]


class SizedImageCenterpointSelectWidget(SizedImageCenterpointWidgetMixIn, MultiWidget):

    def __init__(self, widgets=None, attrs=None):
        widgets = [
            ClearableFileInput(attrs=None),
            Select(
                attrs=attrs,
                choices=CENTERPOINT_CHOICES
            )
        ]
        super(SizedImageCenterpointSelectWidget, self).__init__(widgets, attrs)


class SizedImageCenterpointClickWidget(SizedImageCenterpointWidgetMixIn, MultiWidget):

    def __init__(self, widgets=None, attrs=None):
        widgets = [
            ClearableFileInputWithImagePreview(attrs={'class':'file-chooser'}),
            HiddenInput(
                attrs={'class':'centerpoint-input'}
            )
        ]
        super(SizedImageCenterpointClickWidget, self).__init__(widgets, attrs)

    class Media:
        pass
        css = {
            'all': ('sizedimagefield/css/sizedimagefield.css',),
        }
        js = (
            'sizedimagefield/js/sizedimagefield.js',
        )

    def render(self, name, value, attrs=None):
        rendered = super(SizedImageCenterpointClickWidget, self).render(name, value, attrs)
        to_return = '<div class="sizedimagefield">' + mark_safe(rendered) + '</div>'
        return mark_safe(to_return)
