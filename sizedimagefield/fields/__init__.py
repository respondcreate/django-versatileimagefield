from django.db.models.fields.files import ImageField
from django.utils.translation import ugettext_lazy as _

from .files import SizedImageFieldFile, SizedImageFileDescriptor

class SizedImageField(ImageField):
    attr_class = SizedImageFieldFile
    descriptor_class = SizedImageFileDescriptor
    description = _('Sized Image Field')

    def __init__(self, verbose_name=None, name=None, width_field=None,
            height_field=None, centerpoint_field=None, **kwargs):
        self.centerpoint_field = centerpoint_field
        super(SizedImageField, self).__init__(verbose_name, name, **kwargs)

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
            centerpoint = file.crop_center_point
        else:
            # No file, so clear the centerpoint field.
            centerpoint = None

        # Update the centerpoint field.
        if self.centerpoint_field:
            setattr(instance, self.centerpoint_field, centerpoint)

__all__ = ['SizedImageField']
