Installation
============

Installation is easy with `pip <https://pypi.python.org/pypi/pip>`__:

.. code-block:: bash

    $ pip install django-versatileimagefield

Python Compatibility
--------------------

-  2.7.x
-  3.3.x
-  3.4.x
-  3.5.x
-  3.6.x
-  3.7.x

Django Compatibility
--------------------

-  1.8.x
-  1.9.x
-  1.10.x
-  1.11.x
-  2.0.x
-  2.1.x

Dependencies
------------

-  ``Pillow`` 2.4.x thru 6.0.0

``django-versatileimagefield`` depends on the excellent
`Pillow <https://pillow.readthedocs.io>`__ fork of ``PIL``. If you
already have PIL installed, it is recommended you uninstall it prior to
installing ``django-versatileimagefield``:

.. code-block:: bash

    $ pip uninstall PIL
    $ pip install django-versatileimagefield

.. note:: ``django-versatileimagefield`` will not install ``django``.

.. _settings:

Settings
--------

After installation completes, add ``'versatileimagefield'`` to
``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        # All your other apps here
        'versatileimagefield',
    )

.. _versatileimagefield-settings:

``VERSATILEIMAGEFIELD_SETTINGS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dictionary that allows you to fine-tune how ``django-versatileimagefield`` works:

.. code-block:: python

    VERSATILEIMAGEFIELD_SETTINGS = {
        # The amount of time, in seconds, that references to created images
        # should be stored in the cache. Defaults to `2592000` (30 days)
        'cache_length': 2592000,
        # The name of the cache you'd like `django-versatileimagefield` to use.
        # Defaults to 'versatileimagefield_cache'. If no cache exists with the name
        # provided, the 'default' cache will be used instead.
        'cache_name': 'versatileimagefield_cache',
        # The save quality of modified JPEG images. More info here:
        # https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html#jpeg
        # Defaults to 70
        'jpeg_resize_quality': 70,
        # The name of the top-level folder within storage classes to save all
        # sized images. Defaults to '__sized__'
        'sized_directory_name': '__sized__',
        # The name of the directory to save all filtered images within.
        # Defaults to '__filtered__':
        'filtered_directory_name': '__filtered__',
        # The name of the directory to save placeholder images within.
        # Defaults to '__placeholder__':
        'placeholder_directory_name': '__placeholder__',
        # Whether or not to create new images on-the-fly. Set this to `False` for
        # speedy performance but don't forget to 'pre-warm' to ensure they're
        # created and available at the appropriate URL.
        'create_images_on_demand': True,
        # A dot-notated python path string to a function that processes sized
        # image keys. Typically used to md5-ify the 'image key' portion of the
        # filename, giving each a uniform length.
        # `django-versatileimagefield` ships with two post processors:
        # 1. 'versatileimagefield.processors.md5' Returns a full length (32 char)
        #    md5 hash of `image_key`.
        # 2. 'versatileimagefield.processors.md5_16' Returns the first 16 chars
        #    of the 32 character md5 hash of `image_key`.
        # By default, image_keys are unprocessed. To write your own processor,
        # just define a function (that can be imported from your project's
        # python path) that takes a single argument, `image_key` and returns
        # a string.
        'image_key_post_processor': None,
        # Whether to create progressive JPEGs. Read more about progressive JPEGs
        # here: https://optimus.io/support/progressive-jpeg/
        'progressive_jpeg': False
    }

.. _placehold-it:

``VERSATILEIMAGEFIELD_USE_PLACEHOLDIT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean that signifies whether optional (``blank=True``) ``VersatileImageField`` fields that do not  :ref:`specify a placeholder image <defining-placeholder-images>` should return `placehold.it <http://placehold.it/>`__ URLs.

.. _rendition-key-sets:

``VERSATILEIMAGEFIELD_RENDITION_KEY_SETS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dictionary used to specify 'Rendition Key Sets' that are used for both :doc:`serialization </drf_integration>` or as a way to :doc:`'warm' image files </improving_performance>` so they don't need to be created on demand (i.e. when ``settings.VERSATILEIMAGEFIELD_SETTINGS['create_images_on_demand']`` is set to ``False``) which will greatly improve the overall performance of your app. Here's an example:

.. code-block:: python

    VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
        'image_gallery': [
            ('gallery_large', 'crop__800x450'),
            ('gallery_square_small', 'crop__50x50')
        ],
        'primary_image_detail': [
            ('hero', 'crop__600x283'),
            ('social', 'thumbnail__800x800')
        ],
        'primary_image_list': [
            ('list', 'crop__400x225'),
        ],
        'headshot': [
            ('headshot_small', 'crop__150x175'),
        ]
    }

Each key in ``VERSATILEIMAGEFIELD_RENDITION_KEY_SETS`` signifies a 'Rendition Key Set', a list comprised of 2-tuples wherein the  first position is a serialization-friendly name of an image rendition and the second position is a 'Rendition Key' (which dictates how the original image should be modified).

.. _writing-rendition-keys:

Writing Rendition Keys
^^^^^^^^^^^^^^^^^^^^^^

Rendition Keys are intuitive and easy to write, simply swap in double-underscores for the dot-notated paths you'd use :doc:`in the shell </using_sizers_and_filters>` or :ref:`in templates <template-usage>`. Examples:

.. list-table::
   :widths: 15 35 25 25
   :header-rows: 1

   * - Intended image
     - As 'Rendition Key'
     - In the shell
     - In templates
   * - 400px by 400px Crop
     - ``'crop__400x400'``
     - ``instance.image_field.crop['400x400'].url``
     - ``{{ instance.image_field.crop.400x400 }}``
   * - 100px by 100px Thumbnail
     - ``'thumbnail__100x100'``
     - ``instance.image_field.thumbnail['100x100'].url``
     - ``{{ instance.image_field.thumbnail.100x100 }}``
   * - Inverted Image (Full Size)
     - ``'filters__invert'``
     - ``instance.image_field.filters.invert.url``
     - ``{{ instance.image_field.filters.invert }}``
   * - Inverted Image, 50px by 50px crop
     - ``'filters__invert__crop__50x50'``
     - ``instance.image_field.filters.invert.crop['50x50'].url``
     - ``{{ instance.image_field.filters.invert.crop.50x50 }}``

Using Rendition Key Sets
^^^^^^^^^^^^^^^^^^^^^^^^

Rendition Key sets are useful! Read up on how they can help you...

- ... :ref:`serialize VersatileImageField instances <serialization>` with Django REST Framework.
- ... :doc:`'pre-warm' images to improve performance </improving_performance>`.
