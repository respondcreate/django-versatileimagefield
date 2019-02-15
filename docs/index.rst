.. django-versatileimagefield documentation master file, created by
   sphinx-quickstart on Sun May  4 20:11:25 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======================================================
Welcome to django-versatileimagefield's documentation!
======================================================

.. image:: https://travis-ci.org/respondcreate/django-versatileimagefield.svg?branch=master
    :target: https://travis-ci.org/respondcreate/django-versatileimagefield
    :alt: Travis CI Status

.. image:: https://coveralls.io/repos/github/respondcreate/django-versatileimagefield/badge.svg?branch=master
    :target: https://coveralls.io/github/respondcreate/django-versatileimagefield?branch=master
    :alt: Coverage Status

.. image:: https://img.shields.io/pypi/v/django-versatileimagefield.svg?style=flat
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Latest Version

----

.. rst-class:: intro-paragraph

  A drop-in replacement for django's ``ImageField`` that provides a flexible, intuitive and :doc:`easily-extensible </writing_custom_sizers_and_filters>` interface for creating new images from the one assigned to the field.

  :doc:`Click here for a quick overview </overview>` of what it is, how it works and whether or not it's the right fit for your project.

Compatibility
=============

- Python:

  - 2.7
  - 3.4
  - 3.5
  - 3.6
  - 3.7

.. note:: The 1.2 release dropped support for Python 3.3.x.

- `Django <https://www.djangoproject.com/>`_:

  - 1.8.x
  - 1.9.x
  - 1.10.x
  - 1.11.x
  - 2.0.x
  - 2.1.x

.. note:: The 1.4 release dropped support for Django 1.5.x & 1.6.x.
.. note:: The 1.7 release dropped support for Django 1.7.x.

- `Pillow <https://pillow.readthedocs.io/en/latest/index.html>`_ >=2.4.0,<=6.0.0

- `Django REST Framework <http://www.django-rest-framework.org/>`_:

  - 3.4.x
  - 3.5.x
  - 3.6.x
  - 3.7.x
  - 3.8.x

Code
====

``django-versatileimagefield`` is hosted on `github <https://github.com/WGBH/django-versatileimagefield>`_.


Table of Contents
=================

.. toctree::
   :maxdepth: 4

   overview
   installation
   model_integration
   specifying_ppoi
   using_sizers_and_filters
   writing_custom_sizers_and_filters
   deleting_created_images
   drf_integration
   improving_performance

Release Notes
=============
1.10
^^^^
- Squashed a bug that prevented calling ``len()`` on ``InMemoryUploadedFile`` instances. This change will help make post processing tasks for newly uploaded images – like uploading files to S3 or other remote storage – more straight-forward. Thanks, `@jxltom <https://github.com/jxltom>`_!
- Added Python 3.7.x compatibility. Thanks, `@NyanKiyoshi <https://github.com/NyanKiyoshi>`_!
- Added Django 2.1.x and Django REST Framework 3.8.x compatibility.
- Added Pillow 6.0.x compatibility.

1.9
^^^
- Fixed a 'race condition' bug that intermittently arose in some cloud storage providers which caused ``VersatileImageField`` to fail when attempting to create a sized url from an image that hadn't finished uploading. A big thanks to `@camflan <https://github.com/camflan>`_ for the stellar work (especially the improvements he contributed to the test suite)!
- Added Django 2.0.x and Django REST Framework 3.7.x compatibility.
- Added Pillow 5.0.x compatibility.

1.8.1
^^^^^
- Updated Pillow dependency. Pillow 2.4.0 thru 4.3.0 now supported in Python 2.7, 3.4, 3.5 and 3.6.

1.8
^^^
- Excluded tests from PyPI releases (thanks, `@matthiask <https://github.com/matthiask>`_!).
- Fixed a bug with the widget if thumbnailing failed or crashed (thanks again, `@matthiask <https://github.com/matthiask>`_!)
- Added a note about import problems when adding a new sizer/filter in Python 2.7 (thanks, `@chubz <https://github.com/chubz>`_!).
- Added LICENSE to package manifest (thanks, `@sannykr <https://github.com/sannykr>`_!).

1.7.1
^^^^^
- Fixed a bug that prevented VersatileImageField from working when ``null=True`` with Django 1.11 (thanks, `@szewczykmira <https://github.com/szewczykmira>`_!).

1.7.0
^^^^^
- Added support for Django 1.11 (thanks, `@slurms <https://github.com/slurms>`_ and `@matthiask <https://github.com/matthiask>`_!).

1.6.3
^^^^^
- Added support for Pillow 4.0 and Python 3.6 (thanks, `@aleksihakli <https://github.com/aleksihakli>`_!)
- Improved docs for writing custom sizers and filters (thanks, `@njamaleddine <https://github.com/njamaleddine>`_!)

1.6.2
^^^^^
- Added support for Pillow 3.4.2

1.6.1
^^^^^
- Logs are now created when thumbnail generation fails (thanks, `@artursmet <https://github.com/artursmet>`_!!!).
- Added support for Django 1.10.x and djangorestframework 3.5.x.
- Fixed a bug that caused :ref:`delete_all_created_images() <deleting-multiple-renditions>` to fail on field instances that didn't have filtered, sized & filtered+sized images. 

1.6
^^^
- Fixed a bug that prevented sized images from deleting properly when the field they were associated with was using a custom ``upload_to`` function. If you are using a custom ``SizedImage`` subclass on your project then be sure to check out :ref:`this section <ensuring-sized-images-deleted>` in the docs. (Thanks, `@Mortal <https://github.com/Mortal>`_!)

1.5
^^^
- Fixed a bug that was causing placeholder images to serialize incorrectly with ``VersatileImageFieldSerializer`` (thanks, `@romanosipenko <https://github.com/romanosipenko>`_!).
- Ensured embedded ICC profiles are preserved when creating new images (thanks, `@gbts <https://github.com/gbts>`_!).
- Added support for `progressive JPEGs <https://optimus.io/support/progressive-jpeg/>`_ (more info :ref:`here <versatileimagefield-settings>`).

1.4
^^^
- Included JPEG resize quality to sized image keys.
- Added ``VERSATILEIMAGEFIELD_SETTINGS['image_key_post_processor']`` setting for specifying a function that will post-process sized image keys to create simpler/cleaner filenames. ``django-versatileimagefield`` ships with two built-in post processors: ``'versatileimagefield.processors.md5'`` and ``'versatileimagefield.processors.md5_16'`` (more info :ref:`here <versatileimagefield-settings>`).

1.3
^^^
- Added the ability to delete images & cache entries created by a ``VersatileImageField`` both :ref:`individually <deleting-individual-renditions>` and :ref:`in bulk <deleting-multiple-renditions>`. Relevant docs :doc:`here </deleting_created_images>`.

1.2.2
^^^^^
- Fixed a critical bug that broke initial project setup (i.e. when ``django.setup()`` is run) when an `app config <https://docs.djangoproject.com/en/1.9/ref/applications/>`_ path was included in ``INSTALLED_APPS`` (as opposed to a 'vanilla' python module).

1.2.1
^^^^^
- Fixed a bug that caused ``collectstatic`` to fail when using placeholder images with external storage, like Amazon S3 (thanks, `@jelko <https://github.com/jelko>`_!).
- ``VersatileImageField`` now returns its placeholder URL if ``.url`` is accessed directly (previously only placeholder images were returned if a sizer or filter was accessed). Thanks (again), `@jelko <https://github.com/jelko>`_!

1.2
^^^
- Fixed a bug that caused ``collectstatic`` to fail when using ``ManifestStaticFilesStorage`` (thanks, `@theskumar <https://github.com/theskumar>`_!).
- Dropped support for Python 3.3.x.
- Added support for Django 1.9.x.

1.1
^^^
- Re-added support for Django 1.5.x (by request, support for Django 1.5.x was previously dropped in the 0.4 release). If you're using ``django-versatileimagefield`` on a Django 1.5.x project please be sure to read :ref:`this bit of documentation <django-15-admin-note>`.
- Added support for Django REST Framework 3.3.x.

1.0.6
^^^^^
- Updated ``VersatileImageFieldSerializer`` to serve image URLs as absolute URIs (if its associated field's storage class isn't doing so already).

  - Formerly: /media/headshots/jane_doe_headshot.jpg
  - Now: http://localhost:8000/media/headshots/jane_doe_headshot.jpg

1.0.5
^^^^^
- Fixed image preview on form validation errors (thanks, `@securedirective <https://github.com/securedirective>`_!).

1.0.4
^^^^^
- Finessed/improved widget functionality for both optional and 'PPOI-less' fields (thanks, `@SebCorbin <https://github.com/SebCorbin>`_!).

1.0.3
^^^^^
- Addressed Django `1.9 deprecation warnings <https://docs.djangoproject.com/en/1.8/internals/deprecation/#deprecation-removed-in-1-9>`_ (``get_cache`` and ``importlib``)
- Enabled ``VersatileImageField`` formfield to be overriden via ``**kwargs``

1.0.2
^^^^^
- Removed clear checkbox from widgets on required fields.

1.0.1
^^^^^
- Squashed a `critical bug <https://github.com/WGBH/django-versatileimagefield/issues/13>`_ in `OnDiscPlaceholderImage`

1.0
^^^
- Added support for Django 1.8.
- Numerous documentation edits/improvements.

0.6.2
^^^^^
- Squashed a bug that caused the :ref:`javascript 'click' widget <ppoi-formfield>` to fail to initialize correctly when multiple VersatileImageFields were displayed on the same page in the admin.
- Added `django.contrib.staticfiles <https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_ integration to widgets.

0.6.1
^^^^^
- Squashed a bug that was throwing an ``AttributeError`` when uploading new images.

0.6
^^^
- Squashed a bug that raised a ``ValueError`` in the admin when editing a model instance with a ``VersatileImageField`` that specified ``ppoi_field``, ``width_field`` and ``height_field``.
- Admin 'click' widget now works in Firefox.
- ``django-versatileimagefield`` is now available for installation via `wheel <https://wheel.readthedocs.io/en/latest/>`_.

0.5.4
^^^^^
- Squashed a bug that was causing the admin 'click' widget to intermittently fail
- Simplified requirements installation (which makes django-versatileimagefield installable by ``pip<=1.6``)

0.5.3
^^^^^
- Changed ``PPOIField`` to be ``editable=False`` by default to address `a bug <https://github.com/WGBH/django-versatileimagefield/issues/7>`_ that consistently raised ``ValidationError`` in ModelForms and the admin

0.5.2
^^^^^
- Squashed a bug that prevented ``PPOIField`` from serializing correctly

0.5.1
^^^^^
- Squashed an installation bug with ``pip`` 6+

0.5
^^^
- Added Python 3.3 & 3.4 compatibility
- Improved cropping with extreme PPOI values

0.4
^^^
- Dropped support for Django 1.5.x
- Introducing per-field :ref:`placeholder image <defining-placeholder-images>` image support! (Note: global placeholder support has been deprecated.)
- Added the ``VERSATILEIMAGEFIELD_USE_PLACEHOLDIT`` setting (:ref:`docs <placehold-it>`)

0.3.1
^^^^^
- Squashed a pip installation bug.

0.3
^^^
-  Added a test suite with `Travis CI <https://travis-ci.org/WGBH/django-versatileimagefield>`_ and `coveralls <https://coveralls.io/r/WGBH/django-versatileimagefield>`_ integration.
-  Introduced support for :doc:`Django REST Framework 3.0 </drf_integration>` serialization.

0.2.1
^^^^^
-  Ensuring :ref:`admin widget <ppoi-formfield>`-dependent thumbnail images are created even if ``VERSATILEIMAGEFIELD_SETTINGS['create_on_demand']`` is set to ``False``

0.2
^^^
-  Introduced :doc:`Django REST Framework support </drf_integration>`!
-  Added ability to turn off on-demand image creation and pre-warm images to :doc:`improve performance </improving_performance>`.

0.1.5
^^^^^
-  Squashed ``CroppedImage`` bug that was causing black stripes to appear on crops of images with PPOI values that were to the right and/or bottom of center (greater-than 0.5).

0.1.4
^^^^^

-  Overhauled how ``CroppedImage`` processes PPOI value when creating cropped images. This new approach yields significantly more accurate results than using the previously utilized ``ImageOps.fit`` function, especially when dealing with PPOI values located near the edges of an image *or* aspect ratios that differ significantly from the original image.
-  Improved PPOI validation
-  Squashed unset ``VERSATILEIMAGEFIELD_SETTINGS['global_placeholder_image']`` bug.
-  Set ``crop`` Sizer default resample to PIL.Image.ANTIALIAS

0.1.3
^^^^^

-  Added support for auto-rotation during pre-processing as dictated by 'Orientation' EXIF data, if available.
-  Added release notes to docs

0.1.2
^^^^^

-  Removed redundant javascript from ppoi 'click' widget (thanks, `@theskumar <https://github.com/theskumar>`_!)

0.1.1
^^^^^

-  Converted giant README into Sphinx-friendly RST
-  Docs added to readthedocs

0.1
^^^

-  Initial open source release
