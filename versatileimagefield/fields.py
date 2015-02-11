from __future__ import unicode_literals

import os

from django.conf import settings
from django.db.models import SubfieldBase
from django.db.models.fields import CharField
from django.db.models.fields.files import ImageField
from django.utils.six import add_metaclass
from django.utils.translation import ugettext_lazy as _

from .files import VersatileImageFieldFile, VersatileImageFileDescriptor
from .forms import SizedImageCenterpointClickDjangoAdminField
from .placeholder import OnStoragePlaceholderImage
from .settings import VERSATILEIMAGEFIELD_PLACEHOLDER_DIRNAME
from .validators import validate_ppoi

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [],
        [
            "^versatileimagefield\.fields\.VersatileImageField",
            "^versatileimagefield\.fields\.PPOIField",
        ]
    )


class VersatileImageField(ImageField):
    attr_class = VersatileImageFieldFile
    descriptor_class = VersatileImageFileDescriptor
    description = _('Versatile Image Field')

    def __init__(self, verbose_name=None, name=None, width_field=None,
                 height_field=None, ppoi_field=None, placeholder_image=None,
                 **kwargs):
        self.ppoi_field = ppoi_field
        super(VersatileImageField, self).__init__(
            verbose_name, name, width_field, height_field, **kwargs
        )
        self._process_placeholder_image(placeholder_image)

    def _process_placeholder_image(self, placeholder_image):
        """
        Ensures the placeholder image has been saved to the same storage class
        as the field in a top level folder with a name specified by
        settings.VERSATILEIMAGEFIELD_SETTINGS['placeholder_directory_name']
        """
        placeholder_image_name = None
        if placeholder_image:
            if isinstance(placeholder_image, OnStoragePlaceholderImage):
                name = placeholder_image.path
            else:
                name = placeholder_image.image_data.name
            placeholder_image_name = os.path.join(
                VERSATILEIMAGEFIELD_PLACEHOLDER_DIRNAME, name
            )
            if not self.storage.exists(placeholder_image_name):
                self.storage.save(
                    placeholder_image_name,
                    placeholder_image.image_data
                )
        self.placeholder_image_name = placeholder_image_name

    def pre_save(self, model_instance, add):
        "Returns field's value just before saving."
        file = super(VersatileImageField, self).pre_save(model_instance, add)
        self.update_ppoi_field(model_instance)
        return file

    def update_ppoi_field(self, instance, *args, **kwargs):
        """
        Updates field's ppoi field, if defined.

        This method is hooked up this field's pre_save method to update
        the ppoi immediately before the model instance (`instance`)
        it is associated with is saved.

        This field's ppoi can be forced to update with force=True,
        which is how VersatileImageField.pre_save calls this method.
        """
        # Nothing to update if the field doesn't have have a ppoi
        # dimension field.
        if not self.ppoi_field:
            return

        # getattr will call the VersatileImageFileDescriptor's __get__ method,
        # which coerces the assigned value into an instance of
        # self.attr_class(VersatileImageFieldFile in this case).
        file = getattr(instance, self.attname)

        # file should be an instance of VersatileImageFieldFile or should be
        # None.
        ppoi = None
        if file and not isinstance(file, tuple):
            if hasattr(file, 'ppoi'):
                ppoi = file.ppoi

        # Update the ppoi field.
        if self.ppoi_field:
            setattr(instance, self.ppoi_field, ppoi)

    def save_form_data(self, instance, data):
        """
        Handles data sent from MultiValueField forms that set
        ppoi values.

        `instance`: The model instance that is being altered via a form
        `data`: The data sent from the form to this field which can be either:
        * `None`: This is unset data from an optional field
        * A two-position tuple: (image_form_data, ppoi_data)
            * `image_form-data` options:
                * `None` the file for this field is unchanged
                * `False` unassign the file form the field
            * `ppoi_data` data structure:
                * `%(x_coordinate)sx%(y_coordinate)s': The ppoi data to
                  assign to the unchanged file

        """
        to_assign = data
        if isinstance(data, tuple):
            # This value is coming from a MultiValueField
            if data[0] is None:
                # This means the file hasn't changed but we need to
                # update the ppoi
                current_field = getattr(instance, self.name)
                if data[1]:
                    current_field.ppoi = data[1]
                to_assign = current_field
            elif data[0] is False:
                # This means the 'Clear' checkbox was checked so we
                # need to empty the field
                to_assign = ''
            else:
                # This means there is a new upload so we need to unpack
                # the tuple and assign the first position to the field
                # attribute
                to_assign = data[0]
        super(VersatileImageField, self).save_form_data(instance, to_assign)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': SizedImageCenterpointClickDjangoAdminField}
        kwargs.update(defaults)
        return super(VersatileImageField, self).formfield(**defaults)


@add_metaclass(SubfieldBase)
class PPOIField(CharField):

    def __init__(self, *args, **kwargs):
        if 'default' not in kwargs:
            kwargs['default'] = '0.5x0.5'
        kwargs['default'] = self.get_prep_value(
            value=validate_ppoi(
                kwargs['default'],
                return_converted_tuple=True
            )
        )
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 20

        super(PPOIField, self).__init__(*args, **kwargs)
        self.validators.append(validate_ppoi)

    def to_python(self, value):
        if value is None:
            value = '0.5x0.5'
        to_return = validate_ppoi(
            value, return_converted_tuple=True
        )
        return to_return

    def get_prep_value(self, value):
        if isinstance(value, tuple):
            value = 'x'.join(str(num) for num in value)
        return value

    def value_to_string(self, obj):
        """
        Prepares field for serialization.
        """
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

__all__ = ['VersatileImageField']
