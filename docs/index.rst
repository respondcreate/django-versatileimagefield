.. django-versatileimagefield documentation master file, created by
   sphinx-quickstart on Sun May  4 20:11:25 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======================================================
Welcome to django-versatileimagefield's documentation!
======================================================

.. image:: https://pypip.in/download/django-versatileimagefield/badge.svg
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Downloads

.. image:: https://pypip.in/version/django-versatileimagefield/badge.svg
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Latest Version

.. image:: https://travis-ci.org/WGBH/django-versatileimagefield.svg
    :target: https://travis-ci.org/WGBH/django-versatileimagefield
    :alt: Travis CI Status

.. image:: https://img.shields.io/coveralls/WGBH/django-versatileimagefield.svg
    :target: https://coveralls.io/r/WGBH/django-versatileimagefield
    :alt: Coverage Status

----

A drop-in replacement for django's ImageField that provides a flexible,
intuitive and easily-extensible interface for quickly creating new
images from the one assigned to your field.


In A Nutshell
=============

-  Creates images anywhere you need them: not just :ref:`in templates <template-usage>`.

-  Non-destructive: Your original image is never modified.

-  :doc:`Sizer and Filter framework </using_sizers_and_filters>`: enables you to quickly add new – or modify existing – ways to create new images:

    +  **Sizers** create images with new sizes and/or aspect ratios
    +  **Filters** change the appearance of an image

-  :ref:`Sizers can be chained onto Filters <using-sizers-with-filters>`: Use case: give me a black-and-white, 400px by 400px square crop of this image.

-  :doc:`Primary Point of Interest (PPOI) support </specifying_ppoi>`: provides a way to specify where the 'primary point of interest' of each individual image is – a value which is available to all Sizers and Filters. Use case: sometimes you want the 'crop centerpoint' to be somewhere other than the center of an image. Includes :ref:`a user-friendly formfield/widget for selecting PPOI <ppoi-formfield>` in the admin (or anywhere else you use ModelForms).

-  Works with any storage: Stores the images it creates within the same storage class as your field . Works great with external storage (like Amazon S3).

-  :doc:`Fully interchangeable </model_integration>` with ``ImageField``: you can easily remove ``VersatileImageField`` from your project's models whenever you'd like.

-  Integrated caching: References to created images are stored in the cache, keeping your application running quickly and efficiently.

-  :doc:`Django REST Framework support </drf_integration>`: Serialize multiple image renditions from a single ``VersatileImageField``.

-  Flexible and fast: On-demand image creation can be toggled in your settings file allowing you to :doc:`turn it off </improving_performance>` when you need your application to run as quickly as possible.

Table of Contents
=================

.. toctree::
   :maxdepth: 4

   installation
   model_integration
   specifying_ppoi
   using_sizers_and_filters
   writing_custom_sizers_and_filters
   drf_integration
   improving_performance

Release Notes
=============

0.2.1
^^^^^
-  Ensuring :ref:`admin widget <ppoi-formfield>`-dependent thumbnail images are created even if ``VERSATILEIMAGEFIELD_SETTINGS['create_on_demand']`` is set to ``False``

0.2
^^^
-  Introducing :doc:`Django REST Framework support </drf_integration>`!
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

Roadmap to v1.0
===============

-  Tests!
-  Python 3 support
-  Custom placeholder image docs
-  Programmatically delete images created by ``VersatileImageField``
   (including clearing their connected cache keys)
