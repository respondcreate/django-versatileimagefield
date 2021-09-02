==========================
django-versatileimagefield
==========================

.. image:: https://github.com/respondcreate/django-versatileimagefield/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/respondcreate/django-versatileimagefield/actions/workflows/tests.yml
    :alt: Github Actions Status

.. image:: https://coveralls.io/repos/github/respondcreate/django-versatileimagefield/badge.svg?branch=master
    :target: https://coveralls.io/github/respondcreate/django-versatileimagefield?branch=master
    :alt: Coverage Status

.. image:: https://img.shields.io/pypi/v/django-versatileimagefield.svg?style=flat
    :target: https://pypi.python.org/pypi/django-versatileimagefield/
    :alt: Latest Version

----

A drop-in replacement for django's ``ImageField`` that provides a flexible, intuitive and easily-extensible interface for creating new images from the one assigned to the field.

`Click here for a quick overview <https://django-versatileimagefield.readthedocs.io/en/latest/overview.html>`_ of what it is, how it works and whether or not it's the right fit for your project.

Compatibility
=============

- Python:

  - 3.6
  - 3.7
  - 3.8
  - 3.9

- `Django <https://www.djangoproject.com/>`_:

  - 2.0.x
  - 2.1.x
  - 2.2.x
  - 3.0.x
  - 3.1.x
  - 3.2.x

**NOTE**: Python 3.6 does not have support for Django <= 1.x.

**NOTE**: The 1.4 release dropped support for Django 1.5.x & 1.6.x.

**NOTE**: The 1.7 release dropped support for Django 1.7.x.

**NOTE**: The 2.1 release dropped support for Django 1.9.x.

- `Pillow <https://pillow.readthedocs.io/en/latest/index.html>`_ >= 2.4.0

- `Django REST Framework <http://www.django-rest-framework.org/>`_:

  - 3.9.x
  - 3.10.x
  - 3.11.x
  - 3.12.x

Documentation
=============

Full documentation available at `Read the Docs <https://django-versatileimagefield.readthedocs.io/en/latest/>`_.

Code
====

``django-versatileimagefield`` is hosted on `github <https://github.com/WGBH/django-versatileimagefield>`_.

Running Tests
=============

If you're running tests on Mac OSX you'll need `libmagic` installed. The recommended way to do this is with ``homebrew``:

.. code-block:: bash

    $ brew install libmagic

Note: Some systems may also be necessary to install the `non-python Pillow build dependencies <https://pillow.readthedocs.io/en/stable/installation.html#external-libraries>`_.

You'll also need ``tox``:

.. code-block:: bash

    $ pip install tox


To run the entire django-versatileimagefield test matrix, that is, run all tests on all supported combination of versions of ``python``, ``django`` and ``djangorestframework``:

.. code-block:: bash

   $ tox

If you just want to run tests against a specific tox environment first, run this command to list all available environments:

.. code-block:: bash

   $ tox -l

Then run this command, substituting ``{tox-env}`` with the environment you want to test:

.. code-block:: bash

   $ tox -e {tox-env}
