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

class InvalidCropCenterPoint(Exception):
    pass

class SizedImageFileDescriptor(ImageFileDescriptor):

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))

        # This is slightly complicated, so worth an explanation.
        # instance.file`needs to ultimately return some instance of `File`,
        # probably a subclass. Additionally, this returned object needs to have
        # the FieldFile API so that users can easily do things like
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
            string_split = file.split(CENTERPOINT_SEPARATOR)
            init_kwargs = {
                'instance':instance,
                'field':self.field
            }
            if len(string_split) > 1:
                init_kwargs.update({
                    'name':string_split[0],
                    'crop_center_point':string_split[1]
                })
            else:
                init_kwargs.update({
                    'name':file
                })

            attr = self.field.attr_class(**init_kwargs)
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
        # the underlying FieldFile might not actually itself have an associated
        # file. So we need to reset the details of the FieldFile in those cases.
        elif isinstance(file, SizedImageFieldFile) and not hasattr(file, 'field'):
            file.instance = instance
            file.field = self.field
            file.storage = self.field.storage

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
            else:
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
        if len(tup) == 2:
            while valid == True:
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

    def __init__(self, *args, **kwargs):
        kwargs.update({'max_length':200})
        super(SizedImageField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'char(200)'

    def get_prep_value(self, value):
        "Returns field's value prepared for saving into a database."
        # Need to convert File objects provided via a form to unicode for database insertion
        if value is None:
            return None
        elif isinstance(value, self.attr_class):
            if hasattr(value, 'name'):
                value = '%(file_storage_path)s%(separator)s%(x_axis)sx%(y_axis)s' % {
                    'file_storage_path':value.name,
                    'separator':CENTERPOINT_SEPARATOR,
                    'x_axis':value.crop_center_point[0],
                    'y_axis':value.crop_center_point[1]
                }
        return six.text_type(value)

