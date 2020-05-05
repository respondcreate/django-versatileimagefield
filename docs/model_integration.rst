Model Integration
=================

The centerpiece of ``django-versatileimagefield`` is its
``VersatileImageField`` which provides a simple, flexible interface for
creating new images from the image you assign to it.

``VersatileImageField`` extends django's ``ImageField`` and can be used
as a drop-in replacement for it. Here's a simple example model that
depicts a typical usage of django's ``ImageField``:

.. code-block:: python
    :emphasize-lines: 2,9-14

    # models.py with `ImageField`
    from django.db import models

    class ImageExampleModel(models.Model):
        name = models.CharField(
            'Name',
            max_length=80
        )
        image = models.ImageField(
            'Image',
            upload_to='images/testimagemodel/',
            width_field='width',
            height_field='height'
        )
        height = models.PositiveIntegerField(
            'Image Height',
            blank=True,
            null=True
        )
        width = models.PositiveIntegerField(
            'Image Width',
            blank=True,
            null=True
        )

        class Meta:
            verbose_name = 'Image Example'
            verbose_name_plural = 'Image Examples'

And here's that same model using ``VersatileImageField`` instead (see highlighted section in the code block below):

.. code-block:: python
    :emphasize-lines: 4,11

    # models.py with `VersatileImageField`
    from django.db import models

    from versatileimagefield.fields import VersatileImageField

    class ImageExampleModel(models.Model):
        name = models.CharField(
            'Name',
            max_length=80
        )
        image = VersatileImageField(
            'Image',
            upload_to='images/testimagemodel/',
            width_field='width',
            height_field='height'
        )
        height = models.PositiveIntegerField(
            'Image Height',
            blank=True,
            null=True
        )
        width = models.PositiveIntegerField(
            'Image Width',
            blank=True,
            null=True
        )

        class Meta:
            verbose_name = 'Image Example'
            verbose_name_plural = 'Image Examples'

.. note:: ``VersatileImageField`` is fully interchangable with
    django.db.models.ImageField_
    which means you can revert back
    anytime you'd like. It's fully-compatible with
    south_ so migrate to your heart's content!

.. _defining-placeholder-images:

Specifying Placeholder Images
-----------------------------

For ``VersatileImageField`` fields that are set to ``blank=True`` you can optionally specify a placeholder image to be used when its sizers and filters are accessed (like a generic silouette for a non-existent user profile image, for instance).

You have two options for specifying placeholder images:

    1. ``OnDiscPlaceholderImage``: If you want to use an image stored on the same disc as your project's codebase.
    2. ``OnStoragePlaceholderImage``: If you want to use an image that can be accessed directly with a django storage class.

.. note:: All placeholder images are transferred-to and served-from the storage class of their associated field.

``OnDiscPlaceholderImage``
~~~~~~~~~~~~~~~~~~~~~~~~~~

A placeholder image that is stored on the same disc as your project's codebase. Let's add a new, optional ``VersatileImageField`` to our example model to demonstrate:

.. code-block:: python
    :emphasize-lines: 2,7,34-39

    # models.py
    import os

    from django.db import models

    from versatileimagefield.fields import VersatileImageField
    from versatileimagefield.placeholder import OnDiscPlaceholderImage

    class ImageExampleModel(models.Model):
        name = models.CharField(
            'Name',
            max_length=80
        )
        image = VersatileImageField(
            'Image',
            upload_to='images/testimagemodel/',
            width_field='width',
            height_field='height'
        )
        height = models.PositiveIntegerField(
            'Image Height',
            blank=True,
            null=True
        )
        width = models.PositiveIntegerField(
            'Image Width',
            blank=True,
            null=True
        )
        optional_image = VersatileImageField(
            'Optional Image',
            upload_to='images/testimagemodel/optional/',
            blank=True,
            placeholder_image=OnDiscPlaceholderImage(
                path=os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'placeholder.gif'
                )
            )
        )

        class Meta:
            verbose_name = 'Image Example'
            verbose_name_plural = 'Image Examples'

.. note:: In the above example the ``os`` library was used to determine the on-disc path of an image (``placeholder.gif``) that was stored in the same directory as ``models.py``.

Where ``OnDiscPlaceholderImage`` saves images to
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All placeholder images are automatically saved into the same storage as the field they are associated with into a top-level-on-storage directory named by the ``VERSATILEIMAGEFIELD_SETTINGS['placeholder_directory_name']`` setting (defaults to ``'__placeholder__'`` :ref:`docs <versatileimagefield-settings>`).

Placeholder images defined by ``OnDiscPlaceholderImage`` will simply be saved into the placeholder directory (defaults to ``'__placeholder__'`` :ref:`docs <versatileimagefield-settings>`). The placeholder image defined in the example above would be saved to ``'__placeholder__/placeholder.gif'``.

``OnStoragePlaceholderImage``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A placeholder image that can be accessed with a django storage class. Example:

.. code-block:: python
    :emphasize-lines: 5,32-34

    # models.py
    from django.db import models

    from versatileimagefield.fields import VersatileImageField
    from versatileimagefield.placeholder import OnStoragePlaceholderImage

    class ImageExampleModel(models.Model):
        name = models.CharField(
            'Name',
            max_length=80
        )
        image = VersatileImageField(
            'Image',
            upload_to='images/testimagemodel/',
            width_field='width',
            height_field='height'
        )
        height = models.PositiveIntegerField(
            'Image Height',
            blank=True,
            null=True
        )
        width = models.PositiveIntegerField(
            'Image Width',
            blank=True,
            null=True
        )
        optional_image = VersatileImageField(
            'Optional Image',
            upload_to='images/testimagemodel/optional/',
            blank=True,
            placeholder_image=OnStoragePlaceholderImage(
                path='images/placeholder.gif'
            )
        )

        class Meta:
            verbose_name = 'Image Example'
            verbose_name_plural = 'Image Examples'

By default, ``OnStoragePlaceholderImage`` will look look for this image in your default storage class (as determined by default_storage_) but you can explicitly specify a custom storage class with the optional keyword argument ``storage``:

.. code-block:: python
    :emphasize-lines: 7,36

    # models.py
    from django.db import models

    from versatileimagefield.fields import VersatileImageField
    from versatileimagefield.placeholder import OnStoragePlaceholderImage

    from .storage import CustomStorageCls

    class ImageExampleModel(models.Model):
        name = models.CharField(
            'Name',
            max_length=80
        )
        image = VersatileImageField(
            'Image',
            upload_to='images/testimagemodel/',
            width_field='width',
            height_field='height'
        )
        height = models.PositiveIntegerField(
            'Image Height',
            blank=True,
            null=True
        )
        width = models.PositiveIntegerField(
            'Image Width',
            blank=True,
            null=True
        )
        optional_image = VersatileImageField(
            'Optional Image',
            upload_to='images/testimagemodel/optional/',
            blank=True,
            placeholder_image=OnStoragePlaceholderImage(
                path='images/placeholder.gif',
                storage=CustomStorageCls()
            )
        )

        class Meta:
            verbose_name = 'Image Example'
            verbose_name_plural = 'Image Examples'

Where ``OnStoragePlaceholderImage`` saves images to
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Placeholder images defined by ``OnStoragePlaceholderImage`` will be saved into the placeholder directory (defaults to ``'__placeholder__'`` :ref:`docs <versatileimagefield-settings>`) within the same folder heirarchy as their original storage class. The placeholder image used in the example above would be saved to ``'__placeholder__/image/placeholder.gif``.

.. _django.db.models.ImageField: https://docs.djangoproject.com/en/dev/ref/models/fields/#imagefield
.. _south: https://south.readthedocs.io/en/latest/index.html
.. _default_storage: https://docs.djangoproject.com/en/dev/topics/files/#file-storage
