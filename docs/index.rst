.. django-versatileimagefield documentation master file, created by
   sphinx-quickstart on Sun May  4 20:11:25 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======================================================
Welcome to django-versatileimagefield's documentation!
======================================================

.. image:: https://travis-ci.org/WGBH/django-versatileimagefield.svg?branch=master
    :target: https://travis-ci.org/WGBH/django-versatileimagefield
    :alt: Travis CI Status

.. image:: https://img.shields.io/coveralls/WGBH/django-versatileimagefield.svg?style=flat
    :target: https://coveralls.io/r/WGBH/django-versatileimagefield
    :alt: Coverage Status

.. image:: https://img.shields.io/pypi/dm/django-versatileimagefield.svg?style=flat
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Downloads

.. image:: https://img.shields.io/pypi/v/django-versatileimagefield.svg?style=flat
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/django-versatileimagefield/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Supported Python versions

.. image:: https://pypip.in/wheel/django-versatileimagefield/badge.svg
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Wheel Status

----

.. rst-class:: intro-paragraph

  A drop-in replacement for django's ``ImageField`` that provides a flexible, intuitive and :doc:`easily-extensible </writing_custom_sizers_and_filters>` interface for creating new images from the one assigned to the field.

  :doc:`Click here for a quick overview </overview>` of what it is, how it works and whether or not it's the right fit for your project.

Compatibility
=============

- Python 2.7, 3.3 or 3.4
- `Django <https://www.djangoproject.com/>`_ 1.6.x, 1.7.x or 1.8.x
- `Pillow <http://pillow.readthedocs.org/en/latest/index.html>`_ >= 2.4.0
- `Django REST Framework <http://www.django-rest-framework.org/>`_ 2.3.14, 2.4.4, 3.0.x, 3.1.x

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
   drf_integration
   improving_performance

Release Notes
=============

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
- ``django-versatileimagefield`` is now available for installation via `wheel <http://wheel.readthedocs.org/en/latest/>`_.

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

-  Removed redundant javascript from ppoi 'click' widget (thanks, `@skumar <https://github.com/theskumar>`_!)

0.1.1
^^^^^

-  Converted giant README into Sphinx-friendly RST
-  Docs added to readthedocs

0.1
^^^

-  Initial open source release
