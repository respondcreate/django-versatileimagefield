.. django-versatileimagefield documentation master file, created by
   sphinx-quickstart on Sun May  4 20:11:25 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======================================================
Welcome to django-versatileimagefield's documentation!
======================================================

A drop-in replacement for django's ImageField that provides a flexible,
intuitive and easily-extensible interface for quickly creating new
images from the one assigned to your field.

Current Release
===============

0.1.1

In A Nutshell
=============

-  Creates images anywhere you need them: not just in templates.

-  Non-destructive: Your original image is never modified.

-  :doc:`Sizer and Filter framework </using_sizers_and_filters>`: enables you to quickly add new – or modify existing – ways to create new images:

    +  **Sizers** create images with new sizes and/or aspect ratios
    +  **Filters** change the appearance of an image

-  :ref:`Sizers can be chained onto Filters <using-sizers-with-filters>`: Use case: give me a black-and-white, 400px by 400px square crop of this image.

-  :doc:`Primary Point of Interest (PPOI) support </specifying_ppoi>`: provides a way to specify where the 'primary point of interest' of each individual image is – a value which is available to all Sizers and Filters. Use case: sometimes you want the 'crop centerpoint' to be somewhere other than the center of an image. Includes :ref:`a user-friendly formfield/widget for selecting PPOI <ppoi-formfield>` in the admin (or anywhere else you use ModelForms).

-  Works with any storage: Stores the images it creates within the same storage class as your field (just like django's ``FileField`` & ``ImageField``). Works great with a local filesystem or external storage (like Amazon S3).

-  Fully interchangeable with ``ImageField``: you can easily remove VersatileImageField from your project's models whenever you'd like.

-  Integrated caching: References to created images are stored in the cache, keeping your application running quickly and efficiently.

Table of Contents
=================

.. toctree::
   :maxdepth: 4

   installation
   model_integration
   specifying_ppoi
   using_sizers_and_filters
   writing_custom_sizers_and_filters

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

TODO for v0.2
=============

-  Tests!
-  Placeholder docs
-  Programmatically delete images created by ``VersatileImageField``
   (including clearing their connected cache keys)
-  Management command for auto-generating sets of images (and
   pre-warming the cache)
-  Templatetags for sizing/filtering static images

