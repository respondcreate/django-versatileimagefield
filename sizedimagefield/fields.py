from django.conf import settings
from django.core.files.base import File
from django.core.files.images import ImageFile
from django.db.models.fields.files import (
    ImageField,
    ImageFieldFile,
    ImageFileDescriptor
)
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from .datastructures import (
    CroppedImage,
    ScaledImage
)

CENTERPOINT_SEPARATOR = '__CENTERPOINT__'

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [],
        [
            "^sizedimagefield\.fields\.SizedImageField",
        ]
    )

class InvalidCropCenterPoint(Exception):
    pass

class SizedImageFileDescriptor(ImageFileDescriptor):

    def __set__(self, instance, value):
        previous_file = instance.__dict__.get(self.field.name)
        super(SizedImageFileDescriptor, self).__set__(instance, value)

        # Updating centerpoint_field on attribute set
        if previous_file is not None:
            self.field.update_centerpoint_field(instance, force=True)

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))

        # This is slightly complicated, so worth an explanation.
        # instance.file`needs to ultimately return some instance of `File`,
        # probably a subclass. Additionally, this returned object needs to have
        # the SizedImageFieldFile API so that users can easily do things like
        # instance.file.path and have that delegated to the file storage engine.
        # Easy enough if we're strict about assignment in __set__, but if you
        # peek below you can see that we're not. So depending on the current
        # value of the field we have to dynamically construct some sort of
        # "thing" to return.

        # The instance dict contains whatever was originally assigned
        # in __set__.
        file = instance.__dict__[self.field.name]

        # If this value is a string (instance.file = "path/to/file") or None
        # then we simply wrap it with the appropriate attribute class according
        # to the file field. [This is FieldFile for FileFields and
        # ImageFieldFile for ImageFields and their subclasses, like this class;
        # it's also conceivable that user subclasses might also want to subclass
        # the attribute class]. This object understands how to convert a path to
        # a file, and also how to handle None.
        if file is None:
            attr = self.field.attr_class(instance, self.field, file)
            instance.__dict__[self.field.name] = attr

        elif isinstance(file, six.string_types):

            attr = self.field.attr_class(
                instance=instance,
                field=self.field,
                name=file
            )
            # Check if this field has a centerpoint_field assigned
            if attr.field.centerpoint_field:
                # Pulling the current value of the centerpoint_field...
                centerpoint = instance.__dict__[attr.field.centerpoint_field]
                # ...and assigning it to SizedImageField instance
                attr.crop_center_point = centerpoint

            instance.__dict__[self.field.name] = attr

        # Other types of files may be assigned as well, but they need to have
        # the SizedImageFieldFile interface added to them.
        # Thus, we wrap any other type of File inside a SizedImageFieldFile
        # (well, the field's attr_class, which is usually SizedImageFieldFile).
        elif (
                isinstance(
                    file, File
                ) or isinstance(
                    file, ImageFile
                ) or isinstance(
                    file, ImageFieldFile
                )
            ) and not isinstance(file, SizedImageFieldFile):
            file_copy = self.field.attr_class(
                instance=instance,
                field=self.field,
                name=file.name
            )
            file_copy.file = file
            file_copy._committed = False
            instance.__dict__[self.field.name] = file_copy

        # Finally, because of the (some would say boneheaded) way pickle works,
        # the underlying SizedImageFieldFile might not actually itself have an associated
        # file. So we need to reset the details of the FieldFile in those cases.
        elif isinstance(file, SizedImageFieldFile) and not hasattr(file, 'field'):
            file.instance = instance
            file.field = self.field
            file.storage = self.field.storage

            if file.field.centerpoint_field:
                centerpoint = instance.__dict__[file.field.centerpoint_field]
                file.crop_center_point = centerpoint

        # That was fun, wasn't it?
        return instance.__dict__[self.field.name]

class SizedImageMixIn(object):
    crop_center_point = (0.5, 0.5)

    def __init__(self, *args, **kwargs):
        if kwargs.get('crop_center_point', None):
            self.crop_center_point = kwargs['crop_center_point']
            del kwargs['crop_center_point']
        super(SizedImageMixIn, self).__init__(*args, **kwargs)

    def __setattr__(self, key, value):
        if key == 'crop_center_point':
            if not value:
                pass
            else:
                center_point = self.validate_crop_center_point(value)
                if center_point is not False:
                    super(SizedImageMixIn, self).__setattr__(key, center_point)
        else:
            super(SizedImageMixIn, self).__setattr__(key, value)
        return self.crop_center_point

    def validate_crop_center_point(self, val):
        valid = True
        if isinstance(val, tuple):
            to_validate = val
        elif isinstance(val, six.string_types):
            try:
                ccp_split = [float(segment) for segment in val.split('x')]
            except ValueError:
                ccp_split = tuple()
            to_validate = tuple(ccp_split)
        else:
            to_validate = tuple()

        valid = self.validate_crop_center_point_tuple(to_validate)

        if valid:
            return to_validate
        else:
            if getattr(settings, 'DEBUG', True):
                raise InvalidCropCenterPoint("%s is in invalid crop center. `crop_center_point` must provide two coordinates, one for the x axis and one for the y where both values are between 0 and 1. You may pass it as either a two-position tuple like this: (0.5,0.5) or as a string where the two values are separated by an 'x' like this: '0.5x0.5'." % val)
            else:
                return False

    def validate_crop_center_point_tuple(self, tup):
        valid = True
        while valid == True:
            if len(tup) == 2:
                for x in tup:
                    if x >= 0 and x <= 1:
                        pass
                    else:
                        valid = False
                break
            else:
                valid = False
        return valid

    @property
    def scale(self):
        return ScaledImage(
            path_to_image=self.name,
            storage=self.storage
        )

    @property
    def crop(self):
        return CroppedImage(
            path_to_image=self.name,
            storage=self.storage,
            crop_center_point=self.crop_center_point
        )

class SizedImageFieldFile(SizedImageMixIn, ImageFieldFile):
    pass

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
        # (ImageFieldFile in this case).
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

