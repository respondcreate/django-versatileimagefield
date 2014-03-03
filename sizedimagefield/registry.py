from .datastructures import FilteredImage, SizedImage


class AlreadyRegistered(Exception):
    pass


class InvalidSizedImageSubclass(Exception):
    pass


class NotRegistered(Exception):
    pass


class SizedImageFieldRegistry(object):
    """
    A SizedImageFieldRegistry object allows new SizedImage subclasses to be
    dynamically added to all SizedImageFileField instances. New SizedImage
    subclasses are registered with the register() method.
    """

    def __init__(self, name='sizedimage_sizedimage_registry'):
        self._sizedimage_registry = {}  # attr_name -> sizedimage_cls
        self._filter_registry = {}  # attr_name -> filter_cls
        self.name = name

    def register_sizer(self, attr_name, sizedimage_cls):
        """
        Registers a new SizedImage subclass (`sizedimage_cls`) to be used
        via the attribute (`attr_name`)
        """
        if not issubclass(sizedimage_cls, SizedImage):
            raise InvalidSizedImageSubclass(
                'Only subclasses of sizedimagefield.datastructures.SizedImage '
                'may be registered with register_sizer'
            )

        if attr_name in self._sizedimage_registry:
            raise AlreadyRegistered(
                'A SizedImage class is already registered to the %s attribute,'
                'If you would like to override this attribute, use the '
                'unregister method' % attr_name
            )
        else:
            self._sizedimage_registry[attr_name] = sizedimage_cls

    def unregister_sizer(self, attr_name):
        """
        Unregisters the SizedImage subclass currently assigned to `attr_name`.

        If a SizedImage subclass isn't already registered to `attr_name`
        NotRegistered will raise.
        """
        if attr_name not in self._sizedimage_registry:
            raise NotRegistered(
                'No SizedImage subclass is registered to %s' % attr_name
            )
        else:
            del self._sizedimage_registry[attr_name]

    def register_filter(self, attr_name, filterimage_cls):
        """
        Registers a new FilteredImage subclass (`filterimage_cls`) to be used
        via the attribute (filters.`attr_name`)
        """
        if not issubclass(filterimage_cls, FilteredImage):
            raise InvalidSizedImageSubclass(
                'Only subclasses of FilteredImage may be registered as filters'
                'with SizedImageFieldRegistry')

        if attr_name in self._filter_registry:
            raise AlreadyRegistered(
                'A ProcessedImageMixIn class is already registered to the %s '
                'attribute. If you would like to override this attribute, use '
                'the unregister method' % attr_name
            )
        else:
            self._filter_registry[attr_name] = filterimage_cls

    def unregister_filter(self, attr_name):
        """
        Unregisters the FilteredImage subclass currently assigned to
        `attr_name`.

        If a FilteredImage subclass isn't already registered to filters.
        `attr_name` NotRegistered will raise.
        """
        if attr_name not in self._filter_registry:
            raise NotRegistered(
                'No FilteredImage subclass is registered to %s' % attr_name
            )
        else:
            del self._filter_registry[attr_name]

sizedimagefield_registry = SizedImageFieldRegistry()


def autodiscover():
    """
    Auto-discover INSTALLED_APPS sizedimage.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.

    This is an almost 1-to-1 copy of how django's admin application registers
    models
    """

    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's sizedimage module.
        try:
            before_import_sizedimage_registry = copy.copy(
                sizedimagefield_registry._sizedimage_registry
            )
            before_import_filter_registry = copy.copy(
                sizedimagefield_registry._filter_registry
            )
            import_module('%s.sizedimagefield' % app)
        except:
            # Reset the sizedimagefield_registry to the state before the last
            # import as this import will have to reoccur on the next request
            # and this could raise NotRegistered and AlreadyRegistered
            # exceptions (see django ticket #8245).
            sizedimagefield_registry._sizedimage_registry = before_import_sizedimage_registry
            sizedimagefield_registry._filter_registry = before_import_filter_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have a sizedimage module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'sizedimagefield'):
                raise
