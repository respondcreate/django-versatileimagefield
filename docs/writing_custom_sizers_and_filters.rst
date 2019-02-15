=================================
Writing Custom Sizers and Filters
=================================

It's quick and easy to create new Sizers and Filters for use on your
project's ``VersatileImageField`` fields or :ref:`modify already-registered
Sizers and Filters <overriding-existing-sizer-or-filter>`.

Both Sizers and Filters subclass from
``versatileimagefield.datastructures.base.ProcessedImage`` which
provides a :ref:`preprocessing API <preprocessing-api>` as well as all
the business logic necessary to retrieve and save images.

The 'meat' of each Sizer & Filter – what actually modifies the
original image – resides within the ``process_image`` method which
all subclasses must define (not doing so will raise a
``NotImplementedError``). Sizers and Filters expect slightly different
keyword arguments (Sizers required ``width`` and ``height``, for
example) see below for specifics:

.. _writing-a-custom-sizer:

Writing a Custom Sizer
======================

All Sizers should subclass
``versatileimagefield.datastructures.sizedimage.SizedImage`` and, at a
minimum, MUST do two things:

1. Define either the ``filename_key`` attribute or override the
   ``get_filename_key()`` method which is necessary for creating
   unique-to-Sizer-and-size-specified filenames. If neither of the
   aforementioned is done a ``NotImplementedError`` exception will be
   raised.

2. Define a ``process_image`` method that accepts the following
   arguments:

   -  ``image``: a PIL Image instance
   -  ``image_format``: A valid image mime type (e.g. 'image/jpeg').
      This is provided by the ``create_resized_image`` method (which
      calls ``process_image``).
   -  ``save_kwargs``: A ``dict`` of any keyword arguments needed by
      PIL's ``Image.save`` method (initially provided by the
      pre-processing API).
   -  ``width``: An integer representing the width specified by the user
      in the size key.
   -  ``height``: An integer representing the height specified by the
      user in the size key.

For an example, let's take a look at the ``thumbnail`` Sizer (``versatileimagefield.versatileimagefield.ThumbnailImage``):

.. code-block:: python
    :emphasize-lines: 14,16-31
    
    from django.utils.six import BytesIO

    from PIL import Image

    from .datastructures import SizedImage

    class ThumbnailImage(SizedImage):
        """
        Sizes an image down to fit within a bounding box

        See the `process_image()` method for more information
        """

        filename_key = 'thumbnail'

        def process_image(self, image, image_format, save_kwargs,
                          width, height):
            """
            Returns a BytesIO instance of `image` that will fit
            within a bounding box as specified by `width`x`height`
            """
            imagefile = BytesIO()
            image.thumbnail(
                (width, height),
                Image.ANTIALIAS
            )
            image.save(
                imagefile,
                **save_kwargs
            )
            return imagefile

.. important:: ``process_image`` should *always* return a ``BytesIO`` instance. See :ref:`what-process_image-should-return` for more information.

.. _ensuring-sized-images-deleted:

Ensuring Sized Images Can Be Deleted
------------------------------------

If your ``SizedImage`` subclass uses more than just ``filename_key`` to construct filenames than you'll also want to define the ``filename_key_regex`` attribute.

Confused? Let's take a look at ``CroppedImage`` – which includes individual image PPOI values in the images it creates – as an example:

.. code-block:: python
    :emphasize-lines: 9,11-16

    class CroppedImage(SizedImage):
        """
        A SizedImage subclass that creates a 'cropped' image.

        See the `process_image` method for more details.
        """

        filename_key = 'crop'
        filename_key_regex = r'crop-c[0-9-]+__[0-9-]+'

        def get_filename_key(self):
            """Return the filename key for cropped images."""
            return "{key}-c{ppoi}".format(
                key=self.filename_key,
                ppoi=self.ppoi_as_str()
            )

The ``get_filename_key`` method above is what is used by the sizer to create a filename fragment when **creating** images. It combines the ``filename_key`` with an individual image's PPOI value which ensures PPOI changes result in newly created images (which makes sense when you're cropping in respect to PPOI). The ``filename_key_regex`` is a regular expression pattern utilized by the :doc:`file deletion API </deleting_created_images>` in order to find cropped images created from the original image.

.. _writing-a-custom-filter:

Writing a Custom Filter
=======================

All Filters should subclass
``versatileimagefield.datastructures.filteredimage.FilteredImage`` and
only need to define a ``process_image`` method with following
arguments:

-  ``image``: a PIL Image instance
-  ``image_format``: A valid image mime type (e.g. 'image/jpeg'). This
   is provided by the ``create_resized_image()`` method (which calls
   ``process_image``).
-  ``save_kwargs``: A ``dict`` of any keyword arguments needed by PIL's
   ``Image.save`` method (initially provided by the pre-processing API).

For an example, let's take a look at the ``invert`` Filter
(``versatileimagefield.versatileimagefield.InvertImage``):

.. code-block:: python
    :emphasize-lines: 14-24

    from django.utils.six import BytesIO

    from PIL import ImageOps

    from .datastructures import FilteredImage

    class InvertImage(FilteredImage):
        """
        Inverts the colors of an image.

        See the `process_image()` for more specifics
        """

        def process_image(self, image, image_format, save_kwargs={}):
            """
            Returns a BytesIO instance of `image` with inverted colors
            """
            imagefile = BytesIO()
            inv_image = ImageOps.invert(image)
            inv_image.save(
                imagefile,
                **save_kwargs
            )
            return imagefile

.. important:: ``process_image`` should **always** return a ``BytesIO`` instance. See :ref:`what-process_image-should-return` for more information.

.. _what-process_image-should-return:

What ``process_image`` should return
====================================

Any ``process_image`` method you write should *always* return a
``BytesIO`` instance comprised of raw image data. The actual image file
will be written to your field's storage class via the ``save_image``
method. Note how ``save_kwargs`` is passed into PIL's ``Image.save``
method in the examples above, this ensures PIL knows how to write this
data (based on mime type or any other per-filetype specific options
provided by the :ref:`preprocessing API <preprocessing-api>`).

.. _preprocessing-api:

The Pre-processing API
======================

Both Sizers and Filters have access to a pre-processing API that provides
hooks for doing any per-mime-type processing. This allows your Sizers
and Filters to do one thing for JPEGs and another for GIFs, for
instance. One example of this is in how Sizers 'know' how to preserve
transparency for GIFs or save JPEGs as RGB (at the user-defined
quality):

.. code-block:: python

    # versatileimagefield/datastructures/sizedimage.py
    class SizedImage(ProcessedImage, dict):
        "<a bunch of ommited code here>"

        def preprocess_GIF(self, image, **kwargs):
            """
            Receives a PIL Image instance of a GIF and returns 2-tuple:
                * [0]: Original Image instance (passed to `image`)
                * [1]: Dict with a transparency key (to GIF transparency layer)
            """
            return (image, {'transparency': image.info['transparency']})

        def preprocess_JPEG(self, image, **kwargs):
            """
            Receives a PIL Image instance of a JPEG and returns 2-tuple:
                * [0]: Image instance, converted to RGB
                * [1]: Dict with a quality key (mapped to the value of `QUAL` as
                       defined by the `VERSATILEIMAGEFIELD_JPEG_RESIZE_QUALITY`
                       setting)
            """
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return (image, {'quality': QUAL})

All pre-processors should accept one required argument ``image`` (A PIL
Image instance) and ``**kwargs`` (for easy extension by subclasses) and
return a 2-tuple of the image and a dict of any additional keyword
arguments to pass along to PIL's ``Image.save`` method.

Pre-processor Naming Convention
-------------------------------

In order for preprocessor methods to run, they need to be named
correctly via this simple naming convention: ``preprocess_FILETYPE``.
Here's a list of all currently-supported file types:

-  BMP
-  DCX
-  EPS
-  GIF
-  JPEG
-  PCD
-  PCX
-  PDF
-  PNG
-  PPM
-  PSD
-  TIFF
-  XBM
-  XPM

So, if you'd want to write a PNG-specific preprocessor, your Sizer or
Filter would need to define a method named ``preprocess_PNG``.

.. note:: I've only tested ``VersatileImageField`` with PNG, GIF and JPEG
    files; the list above is what PIL supports, for more information
    about per filetype support in PIL `visit
    here <https://infohost.nmt.edu/tcc/help/pubs/pil/formats.html>`__.

.. _registering-sizers-and-filters:

Registering Sizers and Filters
==============================

Registering Sizers and Filters is easy and straight-forward; if you've
ever registered a model with django's ``admin`` you'll feel right at
home.

``django-versatileimagefield`` finds Sizers & Filters within modules named
``versatileimagefield`` – (i.e. ``versatileimagefield.py``)
that are available at the 'top level' of each app on ``INSTALLED_APPS``.

.. caution:: If your project is based on python 2.x you can prevent import problems  
    by including ``from __future__ import absolute_import`` at the top of any files
    related to your custom sizer/filter.

Here's an example:

::

    somedjangoapp/
        __init__.py
        models.py               # Models
        admin.py                # Admin config
        versatileimagefield.py   # Custom Sizers and Filters here

After defining your Sizers and Filters you'll need to register them with
the ``versatileimagefield_registry``. Here's how the ``ThumbnailSizer``
is registered (see the highlighted lines in the following code block for the relevant bits):

.. code-block:: python
    :emphasize-lines: 7,36-38

    # versatileimagefield/versatileimagefield.py
    from django.utils.six import BytesIO

    from PIL import Image

    from .datastructures import SizedImage
    from .registry import versatileimagefield_registry


    class ThumbnailImage(SizedImage):
        """
        Sizes an image down to fit within a bounding box

        See the `process_image()` method for more information
        """

        filename_key = 'thumbnail'

        def process_image(self, image, image_format, save_kwargs,
                          width, height):
            """
            Returns a BytesIO instance of `image` that will fit
            within a bounding box as specified by `width`x`height`
            """
            imagefile = BytesIO()
            image.thumbnail(
                (width, height),
                Image.ANTIALIAS
            )
            image.save(
                imagefile,
                **save_kwargs
            )
            return imagefile

    # Registering the ThumbnailSizer to be available on VersatileImageField
    # via the `thumbnail` attribute
    versatileimagefield_registry.register_sizer('thumbnail', ThumbnailImage)

All Sizers are registered via the ``versatileimagefield_registry.register_sizer`` method. The first
argument is the attribute you want to make the Sizer available at and
the second is the ``SizedImage`` subclass.

Filters are just as easy. Here's how the ``InvertImage`` filter is registered (see the highlighted lines in the following code block for the relevant bits):

.. code-block:: python
    :emphasize-lines: 6,28

    from django.utils.six import BytesIO

    from PIL import ImageOps

    from .datastructures import FilteredImage
    from .registry import versatileimagefield_registry


    class InvertImage(FilteredImage):
        """
        Inverts the colors of an image.

        See the `process_image()` for more specifics
        """

        def process_image(self, image, image_format, save_kwargs={}):
            """
            Returns a BytesIO instance of `image` with inverted colors
            """
            imagefile = BytesIO()
            inv_image = ImageOps.invert(image)
            inv_image.save(
                imagefile,
                **save_kwargs
            )
            return imagefile

    versatileimagefield_registry.register_filter('invert', InvertImage)

All Filters are registered via the
``versatileimagefield_registry.register_filter`` method. The first
argument is the attribute you want to make the Filter available at and
the second is the FilteredImage subclass.

Unallowed Sizer & Filter Names
------------------------------

Sizer and Filter names cannot begin with an underscore as it would
prevent them from being accessible within the template layer.
Additionally, since Sizers are available for use directly on a
``VersatileImageField``, there are some Sizer names that are unallowed;
trying to register a Sizer with one of the following names will result
in a ``UnallowedSizerName`` exception:

-  ``build_filters_and_sizers``
-  ``chunks``
-  ``close``
-  ``closed``
-  ``create_on_demand``
-  ``delete``
-  ``encoding``
-  ``field``
-  ``file``
-  ``fileno``
-  ``filters``
-  ``flush``
-  ``height``
-  ``instance``
-  ``isatty``
-  ``multiple_chunks``
-  ``name``
-  ``newlines``
-  ``open``
-  ``path``
-  ``ppoi``
-  ``read``
-  ``readinto``
-  ``readline``
-  ``readlines``
-  ``save``
-  ``seek``
-  ``size``
-  ``softspace``
-  ``storage``
-  ``tell``
-  ``truncate``
-  ``url``
-  ``validate_ppoi``
-  ``width``
-  ``write``
-  ``writelines``
-  ``xreadlines``

.. _overriding-existing-sizer-or-filter:

Overriding an existing Sizer or Filter
======================================

If you try to register a Sizer or Filter with an attribute name that's
already in use (like ``crop`` or ``thumbnail`` or ``invert``), an
``AlreadyRegistered`` exception will raise.

.. caution:: A Sizer can have the same name as a Filter (since names are only
    required to be unique per type) however it's **not** recommended.

If you'd like to override an already-registered Sizer or Filter just use
either the ``unregister_sizer`` or ``unregister_filter`` methods of
``versatileimagefield_registry``. Here's how you could 'override' the
``crop`` Sizer:

.. code-block:: python

    from versatileimagefield.registry import versatileimagefield_registry

    # Unregistering the 'crop' Sizer
    versatileimagefield_registry.unregister_sizer('crop')
    # Registering a custom 'crop' Sizer
    versatileimagefield_registry.register_sizer('crop', SomeCustomSizedImageCls)

The order that Sizers and Filters register corresponds to their
containing app's position on ``INSTALLED_APPS``. This means that if you
want to override one of the default Sizers or Filters your app needs to
be included after ``'versatileimagefield'``:

.. code-block:: python

    # settings.py
    INSTALLED_APPS = (
        'versatileimagefield',
        'yourcustomapp'  # This app can override the default Sizers and Filters
    )
