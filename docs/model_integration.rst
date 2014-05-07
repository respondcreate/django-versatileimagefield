Model Integration
=================

The centerpiece of ``django-versatileimagefield`` is its
``VersatileImageField`` which provides a simple, flexible interface for
creating new images from the image you assign to it.

``VersatileImageField`` extends django's ``ImageField`` and can be used
as a drop-in replacement for it. Here's a simple example model that
depicts a typical usage of django's ``ImageField``:

.. code-block:: python

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
    :emphasize-lines: 11,12,13,14,15,16

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
    which means you can revert back to using django's ``ImageField``
    anytime you'd like. It's fully-compatible with
    south_ so migrate to your heart's content!

.. _django.db.models.ImageField: https://docs.djangoproject.com/en/dev/ref/models/fields/#imagefield
.. _south: http://south.readthedocs.org/en/latest/index.html
