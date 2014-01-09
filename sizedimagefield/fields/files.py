from django.conf import settings
from django.core.files.base import File
from django.core.files.images import ImageFile
from django.db.models.fields.files import (
    ImageFieldFile,
    ImageFileDescriptor
)
from django.utils import six

from .mixins import SizedImageMixIn

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [],
        [
            "^sizedimagefield\.fields\.SizedImageField",
        ]
    )

class SizedImageFieldFile(SizedImageMixIn, ImageFieldFile):
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
                attr.crop_centerpoint = centerpoint

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
                file.crop_centerpoint = centerpoint

        # That was fun, wasn't it?
        return instance.__dict__[self.field.name]
