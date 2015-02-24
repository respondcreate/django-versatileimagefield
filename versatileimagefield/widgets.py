from __future__ import unicode_literals

from django.forms.widgets import (
    CheckboxInput, ClearableFileInput,
    HiddenInput, MultiWidget, Select
)
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

CENTERPOINT_CHOICES = (
    ('0.0x0.0', 'Top Left'),
    ('0.0x0.5', 'Top Center'),
    ('0.0x1.0', 'Top Right'),
    ('0.5x0.0', 'Middle Left'),
    ('0.5x0.5', 'Middle Center'),
    ('0.5x1.0', 'Middle Right'),
    ('1.0x0.0', 'Bottom Left'),
    ('1.0x0.5', 'Bottom Center'),
    ('1.0x1.0', 'Bottom Right'),
)


class ClearableFileInputWithImagePreview(ClearableFileInput):
    ppoi_label = ugettext_lazy('Primary Point of Interest')
    template_with_clear = (
        '%(clear)s <label class="versatileimagefield-label" '
        'for="%(clear_checkbox_id)s">'
        '%(clear_checkbox_label)s</label>'
    )
    template_with_initial_and_imagepreview = """
    <div class="sizedimage-mod initial">
        <label class="versatileimagefield-label">%(initial_text)s</label>
        %(initial)s
    </div>
    <div class="sizedimage-mod clear">
        %(clear_template)s
    </div>
    <div class="sizedimage-mod preview">
        <label class="versatileimagefield-label">%(ppoi_label)s</label>
        <div class="image-wrap outer">
            <div class="point-stage" id="%(point_stage_id)s"
                 data-image_preview_id="%(image_preview_id)s">
                <div class="ppoi-point" id="%(ppoi_id)s"></div>
            </div>
            <div class="image-wrap inner">
                %(image_preview)s
            </div>
        </div>
    </div>
    <div class="sizedimage-mod new-upload">
        <label class="versatileimagefield-label">%(input_text)s</label>
        %(input)s
    </div>"""

    def get_hidden_field_id(self, name):
        i = name.rindex('_')
        return "id_%s_%d" % (name[:i], int(name[i + 1:]) + 1)

    def image_preview_id(self, name):
        """
        Given the name of the image preview tag, return the HTML id for it.
        """
        return name + '_imagepreview'

    def get_ppoi_id(self, name):
        """
        Given the name of the image preview tag, return the HTML id for it.
        """
        return name + '_ppoi'

    def get_point_stage_id(self, name):
        return name + '_point-stage'

    def image_preview(self, name, value):
        """
        Given the name of the image preview tag, return the HTML id for it.
        """
        # Ensuring admin preview thumbnails are created and available
        value.create_on_demand = True
        return ('<img src="%(sized_url)s" id="%(image_preview_id)s" '
                'data-hidden_field_id="%(hidden_field_id)s" '
                'data-point_stage_id="%(point_stage_id)s" '
                'data-ppoi_id="%(ppoi_id)s" class="sizedimage-preview"/>') % {
            'sized_url': value.thumbnail['300x300'],
            'image_preview_id': self.image_preview_id(name),
            'hidden_field_id': self.get_hidden_field_id(name),
            'point_stage_id': self.get_point_stage_id(name),
            'ppoi_id': self.get_ppoi_id(name)
        }

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': force_text(self.initial_text),
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
            'ppoi_label': self.ppoi_label
        }
        template = '%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(
            name,
            value,
            attrs
        )
        if value and hasattr(value, "url"):
            substitutions['initial'] = format_html('<a href="{0}">{1}</a>',
                                                   value.url,
                                                   force_text(value))
            if value.field.ppoi_field:
                template = self.template_with_initial_and_imagepreview
                point_stage_id = self.get_point_stage_id(name)
                ppoi_id = self.get_ppoi_id(name)
                substitutions['point_stage_id'] = point_stage_id
                substitutions['ppoi_id'] = ppoi_id
                substitutions['image_preview_id'] = self.image_preview_id(name)
                image_preview = self.image_preview(
                    name,
                    value
                )
                substitutions['image_preview'] = image_preview
            else:
                template = self.template_with_initial

            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(
                    checkbox_name
                )
                substitutions['clear_checkbox_id'] = conditional_escape(
                    checkbox_id
                )
                substitutions['clear'] = CheckboxInput().render(
                    checkbox_name,
                    False,
                    attrs={'id': checkbox_id}
                )
                substitutions['clear_template'] = self.template_with_clear % \
                    substitutions
        return mark_safe(template % substitutions)


class SizedImageCenterpointWidgetMixIn(object):

    def decompress(self, value):
        to_return = [None, None]
        if value:
            to_return = [
                value,
                'x'.join(str(num) for num in value.ppoi)
            ]
        return to_return


class VersatileImagePPOISelectWidget(SizedImageCenterpointWidgetMixIn,
                                     MultiWidget):

    def __init__(self, widgets=None, attrs=None):
        widgets = [
            ClearableFileInput(attrs=None),
            Select(
                attrs=attrs,
                choices=CENTERPOINT_CHOICES
            )
        ]
        super(VersatileImagePPOISelectWidget, self).__init__(widgets, attrs)


class VersatileImagePPOIClickWidget(SizedImageCenterpointWidgetMixIn,
                                    MultiWidget):
    image_preview_template = None
    clear_checkbox_template = None

    def __init__(self, widgets=None, attrs=None, image_preview_template=None):
        widgets = (
            ClearableFileInputWithImagePreview(
                attrs={'class': 'file-chooser'},
            ),
            HiddenInput(
                attrs={'class': 'ppoi-input'}
            )
        )
        super(VersatileImagePPOIClickWidget, self).__init__(widgets, attrs)

    class Media:
        css = {
            'all': ('versatileimagefield/css/versatileimagefield.css',),
        }
        js = (
            'versatileimagefield/js/versatileimagefield.js',
        )

    def render(self, name, value, attrs=None):
        rendered = super(VersatileImagePPOIClickWidget, self).render(
            name,
            value,
            attrs
        )
        to_return = '<div class="versatileimagefield">' + \
            mark_safe(rendered) + '</div>'
        return mark_safe(to_return)


class SizedImageCenterpointClickDjangoAdminWidget(
        VersatileImagePPOIClickWidget):

    class Media:
        css = {
            'all': (
                'versatileimagefield/css/versatileimagefield-djangoadmin.css',
            ),
        }


class SizedImageCenterpointClickBootstrap3Widget(
        VersatileImagePPOIClickWidget):
    template_with_initial_and_imagepreview = """
    <div class="form-group">
        <label>%(initial_text)s</label>
        %(initial)s
    </div>
    <div class="form-group sizedimage-mod clear">
        %(clear_template)s
    </div>
    <div class="form-group sizedimage-mod preview">
        <label>%(ppoi_label)s</label>
        <div class="image-wrap outer">
            <div class="point-stage" id="%(point_stage_id)s"
                 data-image_preview_id="%(image_preview_id)s">
                <div class="ppoi-point" id="%(ppoi_id)s"></div>
            </div>
            <div class="image-wrap inner">
                %(image_preview)s
            </div>
        </div>
    </div>
    <div class="form-group sizedimage-mod new-upload">
        <label class="versatileimagefield-label">%(input_text)s</label>
        %(input)s
    </div>"""
    template_with_clear = (
        '<label for="%(clear_checkbox_id)s"'
        'class="checkbox-inline">%(clear)s %(clear_checkbox_label)s'
        '</label>'
    )

    class Media:
        css = {
            'all': (
                'versatileimagefield/css/versatileimagefield-bootstrap3.css',
            ),
        }
