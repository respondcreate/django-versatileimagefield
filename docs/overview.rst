Overview
========

You're probably using an `ImageField <https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.ImageField>`_.

.. code-block:: python

    from django.db import models

    class ExampleModel(models.Model):
        image = models.ImageField(
            'Image',
            upload_to='images/'
        )

You should :doc:`swap it out</model_integration>` for a ``VersatileImageField``. It's better!

.. code-block:: python
    :emphasize-lines: 3,6

    from django.db import models

    from versatileimagefield.fields import VersatileImageField

    class ExampleModel(models.Model):
        image = VersatileImageField(
            'Image',
            upload_to='images/'
        )

Works just like ``ImageField``
------------------------------

Out-of-the-box, ``VersatileImageField`` provides the same functionality as ``ImageField``:

.. list-table::
   :header-rows: 1

   * - Template Code
     - Image
   * - ``<img src="{{ instance.image.url }}" />``
     - .. figure:: /_static/images/the-dowager-countess.jpg
            :alt: An Image


*So what sets it apart?*

Create Images Wherever You Need Them
------------------------------------

A ``VersatileImageField`` can create new images on-demand **both in templates and the shell**.

Let's make a thumbnail image that would fit within a 200px by 200px area:

.. list-table::
   :header-rows: 1

   * - Template Code
     - Image
   * - ``<img src="{{ instance.image.thumbnail.200x200 }}" />``
     - .. figure:: /_static/images/the-dowager-countess-thumbnail-200x200.jpg
            :alt: An Thumbnail Image

No crufty templatetags necessary! Here's how you'd do the same in the shell:

.. code-block:: python
    :emphasize-lines: 3

    >>> from someapp.models import ExampleModel
    >>> instance = ExampleModel.objects.all()[0]
    >>> instance.image.thumbnail['200x200'].url
    '/media/__sized__/images/test-image-thumbnail-200x200.jpg'
    >>> instance.image.thumbnail['200x200'].name
    '__sized__/images/test-image-thumbnail-200x200.jpg'

Crop images at specific sizes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use it to create cropped images, too:

.. list-table::
   :header-rows: 1

   * - Template Code
     - Default, Absolutely Centered Crop
   * - ``<img src="{{ instance.image.crop.400x400 }}" />``
     - .. figure:: /_static/images/the-dowager-countess-crop-c0-5__0-5-400x400.jpg
            :alt: Absolute Center Crop

*Uh-oh. That looks weird.*

Custom, Per-Image Cropping
--------------------------

Don't worry! ``VersatileImageField`` ships with a handy admin-compatible widget that you can use to specify an image's :doc:`Primary Point of Interest (PPOI)</specifying_ppoi>` by clicking on it.

*Note the translucent red square underneath the mouse cursor in the image within the left column below:*

.. list-table::
   :header-rows: 1

   * - Admin Widget PPOI Selection Tool
     - Resultant Cropped Image
   * - .. figure:: /_static/images/ppoi-adjusted.jpg
            :alt: Centered PPOI
     - .. figure:: /_static/images/the-dowager-countess-crop-c0-44__0-22-400x400.jpg
            :alt: Custom PPOI Entered

*Ahhhhh, that's better.*

Filters, too!
-------------

``VersatileImageField`` has :ref:`filters <filters>`, too! Let's create an inverted image:

.. list-table::
   :header-rows: 1

   * - Template Code
     - Image
   * - ``<img src="{{ instance.image.filters.invert.url }}" />``
     - .. figure:: /_static/images/the-dowager-countess__invert__.jpg
            :alt: Inverted Image

You can chain filters and sizers together:

.. list-table::
   :header-rows: 1

   * - Template Code
     - Image
   * - ``<img src="{{ instance.image.filters.invert.thumbnail.200x200 }}" />``
     - .. figure:: /_static/images/the-dowager-countess__invert__-thumbnail-200x200.jpg
            :alt: Inverted Thumbnail Image

Write your own Sizers & Filters
-------------------------------

Making new sizers and filters (or overriding existing ones) is super-easy via the :doc:`Sizer and Filter framework </writing_custom_sizers_and_filters>`.

Django REST Framework Integration
---------------------------------

If you've got an API powered by `Django REST Framework <http://www.django-rest-framework.org/>`_ you can use ``VersatileImageField`` to serve multiple images (in any number of sizes and renditions) from a single field. :doc:`Learn more here </drf_integration>`.

Flexible in development, light-weight in production
---------------------------------------------------

``VersatileImageField``'s on-demand image creation provides maximum flexibility during development but can be :doc:`easily turned off </improving_performance>` so your app performs like a champ in production.

Fully Tested & Python 3 Ready
-----------------------------

``django-versatileimagefield`` is a rock solid, `fully-tested <https://coveralls.io/r/WGBH/django-versatileimagefield>`_ Django app that is compatible with Python 2.7, 3.4 and 3.5 and works with Django 1.5.x thru 1.9.x

Get Started
-----------

You should totally :doc:`try it out </installation>`! It's 100% backwards compatible with ``ImageField`` so you've got nothing to lose!
