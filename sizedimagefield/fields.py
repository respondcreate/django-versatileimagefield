from django.conf import settings
from django.core.exceptions import FieldError, ValidationError
from django.db.models import SubfieldBase
from django.db.models.fields import CharField
from django.db.models.fields.files import ImageField
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from .files import SizedImageFieldFile, SizedImageFileDescriptor
from .forms import SizedImageCenterpointSelectField
from .widgets import SizedImageCenterpointSelectWidget
from .validators import validate_centerpoint, INVALID_CENTERPOINT_ERROR_MESSAGE

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [],
        [
            "^sizedimagefield\.fields\.SizedImageField",
            "^sizedimagefield\.fields\.SizedImageCenterpointField",
        ]
    )

class SizedImageField(ImageField):
    attr_class = SizedImageFieldFile
    descriptor_class = SizedImageFileDescriptor
    description = _('Sized Image Field')

    def __init__(self, verbose_name=None, name=None, width_field=None,
            height_field=None, centerpoint_field=None, **kwargs):
        self.centerpoint_field = centerpoint_field
        super(SizedImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

    def pre_save(self, model_instance, add):
        "Returns field's value just before saving."
        file = super(SizedImageField, self).pre_save(model_instance, add)
        self.update_centerpoint_field(model_instance, force=True)
        return file

    def update_centerpoint_field(self, instance, force=False, *args, **kwargs):
        """
        Updates field's centerpoint field, if defined.

        This method is hooked up this field's pre_save method to update
        the centerpoint immediately before the model instance (`instance`)
        it is associated with is saved.

        This field's centerpoint can be forced to update with force=True,
        which is how SizedImageField.pre_save calls this method.
        """
        # Nothing to update if the field doesn't have have a centerpoint dimension field.
        if not self.centerpoint_field:
            return

        # getattr will call the SizedImageFileDescriptor's __get__ method, which
        # coerces the assigned value into an instance of self.attr_class
        # (SizedImageFieldFile in this case).
        file = getattr(instance, self.attname)

        # Nothing to update if we have no file and not being forced to update.
        if not file and not force:
            return

        centerpoint_filled = not(
            (self.centerpoint_field and not getattr(instance, self.centerpoint_field))
        )
        # When the model instance centerpoint field is filled and force
        # is `False`, we are most likely loading data from the database or
        # updating an image field that already had an image stored. In the
        # first case, we don't want to update the centerpoint field because
        # we are already getting the value from the database. In the second
        # case, we do want to update the centerpoint field and will skip this
        # return because force will be `True` since this method was called
        # from SizedImageFileDescriptor.__set__.
        if centerpoint_filled and not force:
            return

        # file should be an instance of SizedImageFieldFile or should be None.
        if file:
            centerpoint = file.crop_centerpoint
        else:
            # No file, so clear the centerpoint field.
            centerpoint = None

        # Update the centerpoint field.
        if self.centerpoint_field:
            setattr(instance, self.centerpoint_field, centerpoint)

    def save_form_data(self, instance, data):
        """
        Handles data sent from MultiValueField forms that set
        crop_centerpoint values.

        `instance`: The model instance that is being altered via a form
        `data`: The data sent from the form to this field which can be either:
        * `None`: This is unset data from an optional field
        * A two-position tuple: (image_form_data, centerpoint_data)
            * `image_form-data` options:
                * `None` the file for this field is unchanged
                * `False` unassign the file form the field
            * `centerpoint_data` data structure:
                * `%(x_coordinate)sx%(y_coordinate)s': The centerpoint data to
                  assign to the unchanged file

        """
        to_assign = data
        if data is not None:
            if not data:
                # OK, it's False, set to an empty string to clear the field
                to_assign = ''
            # This value is coming from a MultiValueField
            elif isinstance(data, tuple):
                if data[0] is None:
                    current_field = getattr(instance, self.name)
                    current_field.crop_centerpoint = data[1]
                    to_assign = current_field
                elif data[0] is False:
                    to_assign = ''
        super(SizedImageField, self).save_form_data(instance, to_assign)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': SizedImageCenterpointSelectField}
        kwargs.update(defaults)
        return super(SizedImageField, self).formfield(**defaults)

class SizedImageCenterpointField(CharField):
    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        if 'default' not in kwargs:
            kwargs['default'] = '0.5x0.5'
        else:
            try:
                valid_centerpoint = validate_centerpoint(
                    kwargs['default'],
                    return_converted_tuple=True
                )
            except ValidationError:
                raise
            else:
                kwargs['default'] = self.get_prep_value(value=valid_centerpoint)

        super(SizedImageCenterpointField, self).__init__(*args, **kwargs)
        self.validators.append(validate_centerpoint)

    def to_python(self, value):
        if value is None:
            value = '0.5x0.5'
        to_return = validate_centerpoint(
            value, return_converted_tuple=True
        )
        return to_return

    def get_prep_value(self, value):
        if isinstance(value, tuple):
            for_db = 'x'.join(str(num) for num in value)
        else:
            for_db = value
        return for_db

__all__ = ['SizedImageField']
