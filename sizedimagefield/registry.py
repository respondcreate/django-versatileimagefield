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

    def __init__(self, name='sizedimage_sizedimage_registry'):
        self._sizedimage_registry = {}  # attr_name -> sizedimage_cls
        self.name = name

    def register_sizedimage(self, attr_name, sizedimage_cls):
        """
        Registers a new SizedImage subclass (`sizedimage_cls`) to be used
        via the attribute (`attr_name`)
        """
        if not issubclass(sizedimage_cls, SizedImage):
            raise InvalidSizedImageSubclass(
                    'Only subclasses of sizedimagefield.datastructures.SizedImage '
                    'may be registered with the SizedImageRegistry')

        if attr_name in self._sizedimage_registry:
            raise AlreadyRegistered('A SizedImage class is already registered to the %s attribute. '
                'If you would like to override this attribute, use the unregister method' % attr_name)
        else:
            self._sizedimage_registry[attr_name] = sizedimage_cls

    def unregister_sizedimage(self, attr_name):
        """
        Unregisters the SizedImage subclass currently assigned to `attr_name`.

        If a SizedImage subclass isn't already registered to `attr_name` NotRegistered will raise.
        """
        if attr_name not in self._sizedimage_registry:
            raise NotRegistered('No SizedImage subclass is registered to %s' % attr_name)
        else:
            del self._sizedimage_registry[attr_name]

sizedimageregistry = SizedImageRegistry()

def autodiscover():
    """
    Auto-discover INSTALLED_APPS sizedimage.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.

    This is an almost 1-to-1 copy of how django's admin application registers models
    """

    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's sizedimage module.
        try:
            before_import_sizedimage_registry = copy.copy(sizedimageregistry._sizedimage_registry)
            import_module('%s.sizedimage' % app)
        except:
            # Reset the sizedimageregistry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see django ticket #8245).
            sizedimageregistry._sizedimage_registry = before_import_sizedimage_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have a sizedimage module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'sizedimage'):
                raise
