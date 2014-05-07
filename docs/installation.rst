Installation
============

Installation is easy with `pip <https://pypi.python.org/pypi/pip>`__:

.. code-block:: bash

    $ pip install django-versatileimagefield

Dependencies
------------

-  ``django``>=1.5.0
-  ``Pillow`` >= 2.4.0

``django-versatileimagefield`` depends on the excellent
`Pillow <http://pillow.readthedocs.org>`__ fork of ``PIL``. If you
already have PIL installed, it is recommended you uninstall it prior to
installing ``django-versatileimagefield``:

.. code-block:: bash

    $ pip uninstall PIL
    $ pip install django-versatileimagefield

.. note:: ``django-versatileimagefield`` will not install ``django``.

Settings
--------

After installation completes, add ``'versatileimagefield'`` to
``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        # All your other apps here
        'versatileimagefield',
    )

You can fine-tune how ``django-versatileimagefield`` works via the
``VERSATILEIMAGEFIELD_SETTINGS`` setting:

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
        # http://pillow.readthedocs.org/en/latest/handbook/image-file-formats.html#jpeg
        # Defaults to 70
        'jpeg_resize_quality': 70,
        # A path on disc to an image that will be used as a 'placeholder'
        # for non-existant images.
        # If 'global_placeholder_image' is unset, the excellent, free-to-use
        # http://placehold.it service will be used instead.
        'global_placeholder_image': '/path/to/an-image.png',
        # The name of the top-level folder within storage classes to save all
        # sized images. Defaults to '__sized__'
        'sized_directory_name': '__sized__',
        # The name of the directory to save all filtered images within.
        # Defaults to '__filtered__':
        'filtered_directory_name': '__filtered__'
    }
