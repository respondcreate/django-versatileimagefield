Deleting Created Images
=======================

.. note:: The deletion API was added in version 1.3

``VersatileImageField`` ships with a number of useful methods that make it easy to delete unwanted/stale images and/or clear out their associated cache entries.

The docs below all reference this example model:

.. code-block:: python

    # someapp/models.py

    from django.db import models

    from versatileimagefield.fields import VersatileImageField

    class ExampleImageModel(models.Model):
        image = VersatileImageField(upload_to='images/')

.. _deleting-individual-renditions:

Deleting Individual Renditions
------------------------------

Clearing The Cache
~~~~~~~~~~~~~~~~~~

To delete a cache entry associated with a created image just call its ``clear_cache()`` method:

.. code-block:: python
    :emphasize-lines: 5,8,11

    >>> from someapp.models import ExampleImageModel
    >>> instance = ExampleImageModel.objects.get()
    # Deletes the cache entry associated with the 400px by 400px
    # crop of instance.image
    >>> instance.image.crop['400x400'].clear_cache()
    # Deletes the cache entry associated with the inverted
    # filter of instance.image
    >>> instance.image.filters.invert.clear_cache()
    # Deletes the cache entry associated with the inverted + cropped-to
    # 400px by 400px rendition of instance.image
    >>> instance.image.filters.invert.crop['400x400'].clear_cache()

Deleting An Image
~~~~~~~~~~~~~~~~~

To delete a created image just call its ``delete()`` method:

.. code-block:: python
    :emphasize-lines: 5,8,11

    >>> from someapp.models import ExampleImageModel
    >>> instance = ExampleImageModel.objects.get()
    # Deletes the image AND cache entry associated with the 400px by 400px
    # crop of instance.image
    >>> instance.image.crop['400x400'].delete()
    # Deletes the image AND cache entry associated with the inverted
    # filter of instance.image
    >>> instance.image.filters.invert.delete()
    # Deletes the image AND cache entry associated with the inverted +
    # cropped-to 400px by 400px rendition of instance.image
    >>> instance.image.filters.invert.crop['400x400'].delete()

.. note:: Deleting an image will also clear its associated cache entry.

.. _deleting-multiple-renditions:

Deleting Multiple Renditions
----------------------------

Deleting All Sized Images
~~~~~~~~~~~~~~~~~~~~~~~~~

To delete all sized images created by a field use its ``delete_sized_images`` method:

.. code-block:: python
    :emphasize-lines: 4

    >>> from someapp.models import ExampleImageModel
    >>> instance = ExampleImageModel.objects.get()
    # Deletes all sized images and cache entries associated with instance.image
    >>> instance.image.delete_sized_images()

Deleting All Filtered Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To delete all filtered images created by a field use its ``delete_filtered_images`` method:

.. code-block:: python
    :emphasize-lines: 4

    >>> from someapp.models import ExampleImageModel
    >>> instance = ExampleImageModel.objects.get()
    # Deletes all filtered images and cache entries associated with instance.image
    >>> instance.image.delete_filtered_images()

Deleting All Filtered + Sized Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To delete all filtered + sized images created by a field use its ``delete_filtered_sized_images`` method:

.. code-block:: python
    :emphasize-lines: 4

    >>> from someapp.models import ExampleImageModel
    >>> instance = ExampleImageModel.objects.get()
    # Deletes all filtered + sized images and cache entries associated with instance.image
    >>> instance.image.delete_filtered_sized_images()

Deleting ALL Created Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To delete ALL images created by a field (sized, filtered & filtered + sized) use its ``delete_all_created_images`` method:

.. code-block:: python
    :emphasize-lines: 4

    >>> from someapp.models import ExampleImageModel
    >>> instance = ExampleImageModel.objects.get()
    # Deletes ALL images and cache entries associated with instance.image
    >>> instance.image.delete_all_created_images()

.. note:: The original image (``instance.name`` on ``instance.field.storage`` in the above example) will NOT be deleted.

.. _automating-rendition-deletion:

Automating Deletion on ``post_delete``
--------------------------------------

The rendition deleting and cache clearing functionality was written to address the need to delete 'stale' images (i.e. images created from a ``VersatileImageField`` field on a model instance that has since been deleted). Here's a simple example of how to accomplish that with a ``post_delete`` signal receiver:

.. code-block:: python
    :emphasize-lines: 4,11-19

    # someapp/models.py

    from django.db import models
    from django.dispatch import receiver

    from versatileimagefield.fields import VersatileImageField

    class ExampleImageModel(models.Model):
        image = VersatileImageField(upload_to='images/')

    @receiver(models.signals.post_delete, sender=ExampleImageModel)
    def delete_ExampleImageModel_images(sender, instance, **kwargs):
        """
        Deletes ExampleImageModel image renditions on post_delete.
        """
        # Deletes Image Renditions
        instance.image.delete_all_created_images()
        # Deletes Original Image
        instance.image.delete(save=False)

.. warning:: There's no undo for deleting images off a storage object so proceed at your own risk!
