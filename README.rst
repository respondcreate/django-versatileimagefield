==========================
django-versatileimagefield
==========================

.. image:: https://travis-ci.org/WGBH/django-versatileimagefield.svg?branch=master
    :target: https://travis-ci.org/WGBH/django-versatileimagefield
    :alt: Travis CI Status

.. image:: https://img.shields.io/coveralls/WGBH/django-versatileimagefield.svg?style=flat
    :target: https://coveralls.io/r/WGBH/django-versatileimagefield
    :alt: Coverage Status

.. image:: https://pypip.in/py_versions/django-versatileimagefield/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Supported Python versions

.. image:: https://pypip.in/download/django-versatileimagefield/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Downloads

.. image:: https://pypip.in/version/django-versatileimagefield/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Latest Version

----

A drop-in replacement for django's ImageField that provides a flexible,
intuitive and easily-extensible interface for quickly creating new
images from the one assigned to your field.

Documentation
=============

Full documentation available at `Read the Docs <http://django-versatileimagefield.readthedocs.org/en/latest/>`_.

Code
====

``django-versatileimagefield`` is hosted on `github <https://github.com/WGBH/django-versatileimagefield>`_.

In A Nutshell
=============

-  Creates images anywhere you need them: not just `in templates <http://django-versatileimagefield.readthedocs.org/en/latest/using_sizers_and_filters.html#using-sizers-filters-in-templates>`_.

-  Non-destructive: Your original image is never modified.

-  `Sizer and Filter framework <http://django-versatileimagefield.readthedocs.org/en/latest/using_sizers_and_filters.html>`_: enables you to quickly add new – or modify existing – ways to create new images:

    +  **Sizers** create images with new sizes and/or aspect ratios
    +  **Filters** change the appearance of an image

-  `Sizers can be chained onto Filters <http://django-versatileimagefield.readthedocs.org/en/latest/using_sizers_and_filters.html#using-sizers-with-filters>`_: Use case: give me a black-and-white, 400px by 400px square crop of this image.

-  `Primary Point of Interest (PPOI) support <http://django-versatileimagefield.readthedocs.org/en/latest/specifying_ppoi.html>`_: provides a way to specify where the 'primary point of interest' of each individual image is – a value which is available to all Sizers and Filters. Use case: sometimes you want the 'crop centerpoint' to be somewhere other than the center of an image. Includes `a user-friendly formfield/widget for selecting PPOI <http://django-versatileimagefield.readthedocs.org/en/latest/specifying_ppoi.html#formfield-admin-integration>`_ in the admin (or anywhere else you use ModelForms).

-  Works with any storage: Stores the images it creates within the same storage class as your field . Works great with external storage (like Amazon S3).

-  `Fully interchangeable <http://django-versatileimagefield.readthedocs.org/en/latest/model_integration.html>`_ with ``ImageField``: you can easily remove ``VersatileImageField`` from your project's models whenever you'd like.

-  Integrated caching: References to created images are stored in the cache, keeping your application running quickly and efficiently.

-  `Django REST Framework support <http://django-versatileimagefield.readthedocs.org/en/latest/drf_integration.html>`_: Serialize multiple image renditions from a single ``VersatileImageField``.

-  Flexible and fast: On-demand image creation can be toggled in your settings file allowing you to `turn it off <http://django-versatileimagefield.readthedocs.org/en/latest/improving_performance.html>`_ when you need your application to run as quickly as possible.

Roadmap to v1.0
===============

-  Programmatically delete images created by ``VersatileImageField``
   (including clearing their connected cache keys)
