from .datastructures import SizedImage

class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class InvalidSizedImageSubclass(Exception):
    pass

class SizedImageRegistry(object):
    """
    A SizedImageRegistry object allows new SizedImage subclasses to be dynamically
    added to all SizedImageFileField instances. New SizedImage subclasses are registered
    with the register() method.
    """

    def __init__(self, name='sizedimage_registry'):
        self._registry = {}  # attr_name -> sizedimage_cls
        self.name = name

    def register(self, attr_name, sizedimage_cls):
        """
        Registers a new SizedImage subclass (`sizedimage_cls`) to be used
        via the attribute (`attr_name`)
        """
        if not issubclass(sizedimage_cls, SizedImage):
            raise InvalidSizedImageSubclass(
                    'Only subclasses of sizedimagefield.datastructures.SizedImage '
                    'may be registered with the SizedImageRegistry')

        if attr_name in self._registry:
            raise AlreadyRegistered('A SizedImage class is already registered to the %s attribute. '
                'If you would like to override this attribute, use the unregister method' % attr_name)
        else:
            self._registry[attr_name] = sizedimage_cls

    def unregister(self, attr_name):
        """
        Unregisters the SizedImage subclass currently assigned to `attr_name`.

        If a SizedImage subclass isn't already registered to `attr_name` NotRegistered will raise.
        """
        if attr_name not in self._registry:
            raise NotRegistered('No SizedImage subclass is registered to %s' % attr_name)
        else:
            del self._registry[attr_name]

sizedimageregistry = SizedImageRegistry()
