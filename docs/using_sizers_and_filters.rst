========================
Using Sizers and Filters
========================

Where ``VersatileImageField`` shines is in its ability to create new
images on the fly via its Sizer & Filter framework.

Sizers
======

Sizers provide a way to create new images of differing
sizes from the one assigned to the field. ``VersatileImageField`` ships
with two Sizers, ``thumbnail`` and ``crop``.

Each Sizer registered to the :ref:`Sizer registry <registering-sizers-and-filters>` is available as an attribute
on each ``VersatileImageField``. Sizers are ``dict`` subclasses that
only accept precisely formatted keys comprised of two integers –
representing width and height, respectively – separated by an 'x' (i.e.
``['400x400']``). If you send a malformed/invalid key to a Sizer, a
``MalformedSizedImageKey`` exception will raise.

Included Sizers
---------------

thumbnail
^^^^^^^^^

Here's how you would create a thumbnail image that would be constrained
to fit within a 400px by 400px area:

.. code-block:: python
    :emphasize-lines: 6,7,10,11

    # Importing our example Model
    >>> from someapp.models import ImageExampleModel
    # Retrieving a model instance
    >>> example = ImageExampleModel.objects.all()[0]
    # Displaying the path-on-storage of the image currently assigned to the field
    >>> example.image.name
    u'images/testimagemodel/test-image.jpg'
    # Retrieving the path on the field's storage class to a 400px wide
    # by 400px tall constrained thumbnail of the image.
    >>> example.image.thumbnail['400x400'].name
    u'__sized__/images/testimagemodel/test-image-thumbnail-400x400.jpg'
    # Retrieving the URL to the 400px wide by 400px tall thumbnail
    >>> example.image.thumbnail['400x400'].url
    u'/media/__sized__/images/testimagemodel/test-image-thumbnail-400x400.jpg'

.. _on-demand-image-creation:

.. note:: Images are created on-demand. If no image had yet existed at the location required – by either the path (``.name``) *or* URL (``.url``) shown in the highlighted lines above – one would have been created directly before returning it.

Here's how you'd open the thumbnail image we just created as an image file
directly in the shell:

.. code-block:: python

    >>> thumbnail_image = example.image.field.storage.open(
    ...     example.image.thumbnail['400x400'].name
    ... )

.. _crop-sizer:

crop
^^^^

To create images cropped to a specific size, use the ``crop`` Sizer:

.. code-block:: python

    # Retrieving the URL to a 400px wide by 400px tall crop of the image
    >>> example.image.crop['400x400'].url
    u'/media/__sized__/images/testimagemodel/test-image-crop-c0-5__0-5-400x400.jpg'

The ``crop`` Sizer will first scale an image down to its longest side
and then crop/trim inwards, centered on the **Primary Point of
Interest** (PPOI, for short). For more info about what PPOI is and how
it's used see the :doc:`Specifying a Primary Point of Interest
(PPOI) </specifying_ppoi>` section.

How Sized Image Files are Named/Stored
''''''''''''''''''''''''''''''''''''''

All Sizers subclass from
``versatileimagefield.datastructures.sizedimage.SizedImage`` which uses
a unique-to-size-specified string – provided via its
``get_filename_key()`` method – that is included in the filename of each
image it creates.

.. note:: The ``thumbnail`` Sizer simply combines ``'thumbnail'`` with the
    size key passed (i.e. ``'400x400'`` ) while the ``crop`` Sizer
    combines ``'crop'``, the field's PPOI value (as a string) and the
    size key passed; all Sizer 'filename keys' begin and end with dashes
    ``'-'`` for readability.

All images created by a Sizer are stored within the field's ``storage``
class in a top-level folder named ``'__sized__'``, maintaining the same
descendant folder structure as the original image. If you'd like to
change the name of this folder to something other than ``'__sized__'``,
adjust the value of
``VERSATILEIMAGEFIELD_SETTINGS['sized_directory_name']`` within your
settings file.

Sizers are quick and easy to write, for more information about how it's
done, see the :ref:`Writing a Custom Sizer <writing-a-custom-sizer>`
section.

.. _filters:

Filters
=======

Filters create new images that are the same size and aspect ratio as the
original image.

Included Filters
----------------

invert
^^^^^^

The ``invert`` filter will invert the color palette of an image:

.. code-block:: python

    # Importing our example Model
    >>> from someapp.models import ImageExampleModel
    # Retrieving a model instance
    >>> example = ImageExampleModel.objects.all()[0]
    # Returning the path-on-storage to the image currently assigned to the field
    >>> example.image.name
    u'images/testimagemodel/test-image.jpg'
    # Displaying the path (within the field's storage class) to an image
    # with an inverted color pallete from that of the original image
    >>> example.image.filters.invert.name
    u'images/testimagemodel/__filtered__/test-image__invert__.jpg'
    # Displaying the URL to the inverted image
    >>> example.image.filters.invert.url
    u'/media/images/testimagemodel/__filtered__/test-image__invert__.jpg'

As you can see, there's a ``filters`` attribute available on each
``VersatileImageField`` which contains all filters currently registered
to the Filter registry.

.. _using-sizers-with-filters:

Using Sizers with Filters
-------------------------

What makes Filters extra-useful is that they have access to all
registered Sizers:

.. code-block:: python

    # Creating a thumbnail of a filtered image
    >>> example.image.filters.invert.thumbnail['400x400'].url
    u'/media/__sized__/images/testimagemodel/__filtered__/test-image__invert__-thumbnail-400x400.jpg'
    # Creating a crop from a filtered image
    >>> example.image.filters.invert.crop['400x400'].url
    u'/media/__sized__/images/testimagemodel/__filtered__/test-image__invert__-c0-5__0-5-400x400.jpg'

.. note:: Filtered images are created the first time they are directly
    accessed (by either evaluating their ``name``/``url`` attributes or
    by accessing a Sizer attached to it). Once created, a reference is
    stored in the cache for each created image which makes for speedy
    subsequent retrievals.

How Filtered Image Files are Named/Stored
-----------------------------------------

All Filters subclass from
``versatileimagefield.datastructures.filteredimage.FilteredImage`` which
provides a ``get_filename_key()`` method that returns a
unique-to-filter-specified string – surrounded by double underscores,
i.e. ``'__invert__'`` – which is appended to the filename of each image
it creates.

All images created by a Filter are stored within a folder named
``__filtered__`` that sits in the same directory as the original image.
If you'd like to change the name of this folder to something other than
'**filtered**\ ', adjust the value of
``VERSATILEIMAGEFIELD_SETTINGS['filtered_directory_name']`` within your
settings file.

Filters are quick and easy to write, for more information about creating
your own, see the :ref:`Writing a Custom Filter <writing-a-custom-filter>`
section.

.. _template-usage:

Using Sizers / Filters in Templates
===================================

Template usage is straight forward and easy since both attributes and
dictionary keys can be accessed via dot-notation; no crufty templatetags
necessary:

.. code-block:: html

    <!-- Sizers -->
    <img src="{{ instance.image.thumbnail.400x400 }}" />
    <img src="{{ instance.image.crop.400x400 }}" />

    <!-- Filters -->
    <img src="{{ instance.image.filters.invert.url }}" />

    <!-- Filters + Sizers -->
    <img src="{{ instance.image.filters.invert.thumbnail.400x400 }}" />
    <img src="{{ instance.image.filters.invert.crop.400x400 }}" />

.. note:: Using the ``url`` attribute on Sizers is optional in templates. Why?
    All Sizers return an instance of
    ``versatileimagefield.datastructures.sizedimage.SizedImageInstance``
    which provides the sized image's URL via the ``__unicode__()``
    method (which django's templating engine looks for when asked
    to render class instances directly).
