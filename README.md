# django-versatileimagefield #

A drop-in replacement for django's ImageField that provides a flexible, intuitive and easily-extensible interface for quickly creating new images from the one assigned to your field.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](http://doctoc.herokuapp.com/)*

  - [Current Version](#current-version)
  - [In A Nutshell](#in-a-nutshell)
    - [Works Just Like django's `ImageField`](#works-just-like-djangos-imagefield)
    - [Quickly Make New Images On-The-Fly](#quickly-make-new-images-on-the-fly)
      - [Sizers](#sizers)
      - [Filters](#filters)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
    - [Settings](#settings)
  - [Model Integration](#model-integration)
  - [Sizers & Filters](#sizers-&-filters)
    - [Sizers](#sizers-1)
      - [thumbnail](#thumbnail)
      - [crop](#crop)
      - [How Sized Image Files are Named/Stored](#how-sized-image-files-are-namedstored)
    - [Filters](#filters-1)
      - [How Filtered Image Files are Named/Stored](#how-filtered-image-files-are-namedstored)
    - [Using Sizers / Filters in Templates](#using-sizers--filters-in-templates)
    - [Writing Custom Sizers & Filters](#writing-custom-sizers-&-filters)
      - [Writing a Custom Sizer](#writing-a-custom-sizer)
      - [Writing a Custom Filter](#writing-a-custom-filter)
      - [The Pre-processing API](#the-pre-processing-api)
      - [Preprocessor Naming Convention](#preprocessor-naming-convention)
    - [Registering Sizers & Filters for use on `VersatileImageField`](#registering-sizers-&-filters-for-use-on-versatileimagefield)
        - [Overriding an existing Sizer or Filter](#overriding-an-existing-sizer-or-filter)
          - [Unallowed Sizer & Filter Names](#unallowed-sizer-&-filter-names)
  - [Specifying a Primary Point of Interest (PPOI)](#specifying-a-primary-point-of-interest-ppoi)
    - [The PPOIField](#the-ppoifield)
      - [How PPOI is Stored in the Database](#how-ppoi-is-stored-in-the-database)
    - [Setting your PPOI](#setting-your-ppoi)
      - [Via The Shell](#via-the-shell)
      - [Via The Admin](#via-the-admin)
- [TODO](#todo)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

### Current Version ###

0.1

## In A Nutshell ##

A drop-in replacement for django's ImageField that provides a flexible, intuitive and easily-extensible interface for quickly creating new images from the one assigned to your field.

### Works Just Like django's `ImageField` ###

Swap out any fields currently managed by `ImageField` with `VersatileImageField`:

```python
# models.py with `VersatileImageField`
from django.db import models

from versatileimagefield.fields import VersatileImageField

class ImageExampleModel(models.Model):
    name = models.CharField(
        'Name',
        max_length=80
    )
    image = VersatileImageField(
        'Image',
        upload_to='images/testimagemodel/',
        width_field='width',
        height_field='height'
    )
```

No migrations necessary!

### Quickly Make New Images On-The-Fly ###

`VersatileImageField` gives you the ability to make new images from the one assigned to your field (without modifying the original) via its Sizers & Filters.

#### Sizers ####

Want to make a thumbnail image of your original image that will fit within a 400px by 400px area? `VersatileImageField` makes it easy to serve that image in a template:

```html
<img src="{{ object.image.thumbnail.400x400 }}" />
```

Or retrieve the image file directly in the shell:

```python
thumbnail_image = object.image.field.storage.open(
    object.image.thumbnail['400x400'].name
)
```

How about a cropped image instead?

```html
<img src="{{ object.image.crop.400x400 }}" />
```

Cropped images will respect a **Primary Point of Interest** when they trim image data, ensuring the 'right' part of each image you create is always showing. See the [**Specifying a Primary Point of Interest (PPOI)**](#specifying-a-primary-point-of-interest-ppoi) section below for more details on how to set this value on an instance-by-instance basis.

> `VersatileImageField` ships with two Sizers – `crop` and `thumbnail` – but it's super-easy to write your own (see the [Writing a Custom Sizer](#writing-a-custom-sizer) section for more information).

#### Filters ####

Filters give you the ability to modify the pixel data of an image (without changing its size or dimensions). `VersatileImageField` ships with only one filter – `invert` – that inverts the colors of an image:

```html
<!-- Your image with 'regular' colors -->
<img src="{{ object.image.url }}" />

<!-- Your image with inverted colors -->
<img src="{{ object.image.filters.invert.url }}" />
```

Filters have access to all Sizers, too!

```html
<!-- A thumbnail of an inverted image -->
<img src="{{ object.image.filters.invert.thumbnail.400x400 }}" />
```

> Writing `Filters` is quick and easy, see the [Writing a Custom Filter](#writing-a-custom-filter) section for more information.

## Installation ##

Installation is easy with [pip](https://pypi.python.org/pypi/pip):

```bash
$ pip install django-versatileimagefield
```

### Dependencies ###

* `Pillow` >= 2.4.0

`django-versatileimagefield` depends on the excellent [`Pillow`](http://pillow.readthedocs.org) fork of `PIL`. If you already have PIL installed, it is recommended you uninstall it prior to installing `django-versatileimagefield`:

```bash
$ pip uninstall PIL
$ pip install django-versatileimagefield
```

### Settings ###

After installation completes, add `'versatileimagefield'` to `INSTALLED_APPS`:

```python
INSTALLED_APPS += ('versatileimagefield',)
```

You can fine-tune how `django-versatileimagefield` works via the `VERSATILEIMAGEFIELD_SETTINGS` setting:

```python
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
```

## Model Integration ##

The centerpiece of `django-versatileimagefield` is its `VersatileImageField` which provides a simple, flexible interface for creating new images from the image you assign to it.

`VersatileImageField` extends django's `ImageField` and can be used as a drop-in replacement for it. Here's a simple example model that depicts a typical usage of django's `ImageField`:

```python
# models.py with `ImageField`
from django.db import models

class ImageExampleModel(models.Model):
    name = models.CharField(
        'Name',
        max_length=80
    )
    image = models.ImageField(
        'Image',
        upload_to='images/testimagemodel/',
        width_field='width',
        height_field='height'
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Image Example'
        verbose_name_plural = 'Image Examples'
```

And here's that same model using `VersatileImageField` instead:

```python
# models.py with `VersatileImageField`
from django.db import models

from versatileimagefield.fields import VersatileImageField

class ImageExampleModel(models.Model):
    name = models.CharField(
        'Name',
        max_length=80
    )
    image = VersatileImageField(
        'Image',
        upload_to='images/testimagemodel/',
        width_field='width',
        height_field='height'
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Image Example'
        verbose_name_plural = 'Image Examples'
```

> ### NOTE ###
> `VersatileImageField` is fully interchangable with [`django.db.models.ImageField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#imagefield) which means you can revert back to using django's `ImageField` anytime you'd like. It's fully-compatible with [`south`](http://south.readthedocs.org/en/latest/index.html) so migrate to your heart's content!

## Sizers & Filters ##

Where `VersatileImageField` shines is in its ability to create new images on the fly via its Sizer & Filter framework.

### Sizers ###

The Sizer framework gives you a way to create new images of differing sizes from the one assigned to the field. `VersatileImageField` ships with two Sizers, `thumbnail` and `crop`.

Each Sizer registered to the Sizer registry is available as an attribute on each `VersatileImageField`. Sizers are `dict` subclasses that only accept precisely formatted keys comprised of two integers – representing width and height, respectively – separated by an 'x' (i.e. `['400x400']'). If you send a malformed/invalid key to a Sizer, a `MalformedSizedImageKey` exception will raise.

#### thumbnail ####

Here's how you would create a thumbnail image that would be constrained to fit within a 400px by 400px area:

```python
# Importing our example Model
>>> from someapp.models import ImageExampleModel
# Retrieving a model instance
>>> example = ImageExampleModel.objects.all()[0]
# Displaying the path-on-storage of the image currently assigned to the field
>>> example.image.name
u'images/testimagemodel/test-image.jpg'
# Retrieving the path on the field's storage class to a 400px wide by 400px tall
# constrained thumbnail of the image
>>> example.image.thumbnail['400x400'].name
u'__sized__/images/testimagemodel/test-image-thumbnail-400x400.jpg'
# Retrieving the URL to the 400px wide by 400px tall thumbnail
>>> example.image.thumbnail['400x400'].url
u'/media/__sized__/images/testimagemodel/test-image-thumbnail-400x400.jpg'
```

If you want to open the created thumbnail image as an image file directly in the shell:

```python
>>> thumbnail_image = example.image.field.storage.open(
    example.image.thumbnail['400x400'].name
)
```

#### crop ####

If you wanted create an image cropped to a specific size, use the `crop` Sizer:

```python
# Retrieving the URL to a 400px wide by 400px tall crop of the image
>>> example.image.crop['400x400'].url
u'/media/__sized__/images/testimagemodel/test-image-crop-c0-5__0-5-400x400.jpg'
```

The `crop` Sizer will first scale an image down to its longest side and then crop/trim inwards, centered on the **Primary Point of Interest** (PPOI, for short). For more info about what PPOI is and how it's used see the [**Specifying a Primary Point of Interest (PPOI)**](#specifying-a-primary-point-of-interest-ppoi) section below.

#### How Sized Image Files are Named/Stored ####

All Sizers subclass from `versatileimagefield.datastructures.sizedimage.SizedImage` which uses a unique-to-size-specified string – provided via its `get_filename_key()` method – that is included in the filename of each image it creates.

> ##### NOTE #####
> The `thumbnail` Sizer simply combines `'thumbnail'` with the size key passed (i.e. `'400x400'` ) while the `crop` Sizer combines `'crop'`, the field's PPOI value (as a string) and the size key passed; all Sizer 'filename keys' begin and end with dashes `'-'` for readability.

All images created by a Sizer are stored within the field's `storage` class in a top-level folder named `'__sized__'`, maintaining the same descendant folder structure as the original image. If you'd like to change the name of this folder to something other than `'__sized__'`, adjust the value of `VERSATILEIMAGEFIELD_SETTINGS['sized_directory_name']` within your settings file.

Sizers are quick and easy to write, for more information about how it's done, see the [Writing a Custom Sizer](#writing-a-custom-section) section below.

### Filters ###

Filters are similar to Sizers in that they create new images but they differ in that they don't modify the size or aspect ratio. An example by way of our `TestImageModel` model:

```python
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
```

As you can see, there's a `filters` attribute available on each `VersatileImageField` which contains all filters currently registered to the Filter registry.

> #### NOTE ####
> `django-versatileimagefield` ships with a single Filter – `invert` – which inverts the colors of an image.

What makes Filters extra-useful is that they have access to all registered Sizers:

```python
# Creating a thumbnail of a filtered image
>>> example.image.filters.invert.thumbnail['400x400'].url
u'/media/images/testimagemodel/__filtered__/test-image__invert__-thumbnail-400x400.jpg'
# Creating a crop from a filtered image
>>> example.image.filters.invert.crop['400x400'].url
u'/media/images/testimagemodel/__filtered__/test-image__invert__-c0-5__0-5-400x400.jpg'
```

> #### When Filtered Images Are Created ####
> Filtered images are created the first time they are directly accessed (by either evaluating their `name`/`url` attributes or by accessing a Sizer attached to it). Once created, a reference is stored in the cache for each created image which makes for speedy subsequent retrievals.

#### How Filtered Image Files are Named/Stored ####

All Filters subclass from `versatileimagefield.datastructures.filteredimage.FilteredImage` which provides a `get_filename_key()` method that returns a unique-to-filter-specified string , surrounded by double underscores, which is appended to the filename of each image it creates.

All images created by a Filter are stored within a folder named `__filtered__` that sits in the same directory as the original image. If you'd like to change the name of this folder to something other than '__filtered__', adjust the value of `VERSATILEIMAGEFIELD_SETTINGS['filtered_directory_name']` within your settings file.

Filters are quick and easy to write, for more information about creating your own, see the [Writing a Custom Filter](#writing-a-custom-filter) section below.

### Using Sizers / Filters in Templates ###

Template usage is straight forward and easy since both attributes and dictionary keys can be accessed via dot-notation; no crufty templatetags necessary:

```html
<!-- Sizers -->
<img src="{{ object.image.thumbnail.400x400 }}" />
<img src="{{ object.image.crop.400x400 }}" />

<!-- Filters -->
<img src="{{ object.image.filters.invert.url }}" />

<!-- Filters + Sizers -->
<img src="{{ object.image.filters.invert.thumbnail.400x400 }}" />
<img src="{{ object.image.filters.invert.crop.400x400 }}" />
```

> ### NOTE ###
> Using the `url` attribute on Sizers is optional in templates. Why? All Sizers return an instance of `versatileimagefield.datastructures.sizedimage.SizedImageInstance` which provides the sized image's URL via the `__unicode__()` method (which django's templating engine looks for when it is asked to render class instances directly).

### Writing Custom Sizers & Filters ###

It's quick and easy to create new Sizers & Filters for use on your project's `VersatileImageField` fields or modify already-registered Sizers & Filters.

Both Sizers & Filters subclass from `versatileimagefield.datastructures.base.ProcessedImage` which provides a pre-processing API (more on that in a bit) as well as all the business logic necessary to retrieve and save images.

The 'meat' of each Sizer & Filter – a.k.a what actually modifies the original image – takes place within the `process_image` method which all subclasses must define (not doing so will raise a `NotImplementedError`). Sizers and Filters expect slightly different keyword arguments (Sizers required `width` and `height` kwargs, for example) see below for specifics:

#### Writing a Custom Sizer ####

All Sizers should subclass `versatileimagefield.datastructures.sizedimage.SizedImage` and, at a minimum, MUST do two things:

1. Define either the `filename_key` attribute or override the `get_filename_key()` method which is necessary for creating unique-to-Sizer-and-size-specified filenames. If neither of the aforementioned is done a `NotImplementedError` exception will be raised.

2. Define a `process_image` method that accepts the following arguments:

    * `image`: a PIL Image instance
    * `image_format`: A valid image mime type (e.g. 'image/jpeg'). This is provided by the `create_resized_image` method (which calls `process_image`).
    * `save_kwargs`: A `dict` of any keyword arguments needed by PIL's `Image.save` method (initially provided by the pre-processing API).
    * `width`: An integer representing the width specified by the user in the size key.
    * `height`: An integer representing the height specified by the user in the size key.

For an example, let's take a look at the Sizer that powers the `thumbnail` sizer (`versatileimagefield.versatileimagefield.ThumbnailImage`):

```python
import StringIO

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
        Returns a StringIO instance of `image` that will fit
        within a bounding box as specified by `width`x`height`
        """
        imagefile = StringIO.StringIO()
        image.thumbnail(
            (width, height),
            Image.ANTIALIAS
        )
        image.save(
            imagefile,
            **save_kwargs
        )
        return imagefile
```

#### Writing a Custom Filter ####

All Filters should subclass `versatileimagefield.datastructures.filteredimage.FilteredImage` and only need to define a `process_filter` method with following arguments:

* `image`: a PIL Image instance
* `image_format`: A valid image mime type (e.g. 'image/jpeg'). This is provided by the `create_resized_image()` method (which calls `process_image`).
* `save_kwargs`: A `dict` of any keyword arguments needed by PIL's `Image.save` method (initially provided by the pre-processing API).

For an example, let's take a look at the `invert` Filter (`versatileimagefield.versatileimagefield.InvertImage`):

```python
import StringIO

from PIL import ImageOps

from .datastructures import FilteredImage

class InvertImage(FilteredImage):
    """
    Inverts the colors of an image.

    See the `process_image()` for more specifics
    """

    filename_key = 'invert'

    def process_image(self, image, image_format, save_kwargs={}):
        """
        Returns a StringIO instance of `image` with inverted colors
        """
        imagefile = StringIO.StringIO()
        inv_image = ImageOps.invert(image)
        inv_image.save(
            imagefile,
            **save_kwargs
        )
        return imagefile
```

> #### IMPORTANT ####
> Any `process_image` method you write should _always_ return a `StringIO` instance comprised of raw image data. The actual image file will be written to your field's storage class via the `save_image` method. Note how `save_kwargs` is passed into PIL's `Image.save` method, this ensures PIL knows how to write this data (based on mime type or any other per-filetype specific options provided by the pre-processing).

#### The Pre-processing API ####

Both Sizers and Filters have access to a pre-processing API that provide hooks for doing any per-mime-type processing. This allows your Sizers and Filters to do one thing for JPEGs and another for GIFs, for instance. One example of this is in how Sizers 'know' how to preserve transparency for GIFs or save JPEGs as RGB (at the user-defined quality):

```python
# versatileimagefield/datastructures/sizedimage.py
class SizedImage(ProcessedImage, dict):
    "..."

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
```

All pre-processors should accept one required argument `image` (A PIL Image instance) and `**kwargs` (for easy extension by subclasses) and return a 2-tuple of the image and a dict of any additional keyword arguments to pass along to PIL's `Image.save` method.

#### Preprocessor Naming Convention ####

In order for preprocessor methods to run, they need to be named correctly via this simple naming convention: `preprocess_FILETYPE`. Here's a list of all currently-supported file types:

* BMP
* DCX
* EPS
* GIF
* JPEG
* PCD
* PCX
* PDF
* PNG
* PPM
* PSD
* TIFF
* XBM
* XPM

So, if you'd want to write a PNG-specific preprocessor, your Sizer or Filter would need to define a method named `preprocess_PNG`.

> ##### NOTE #####
> I've only tested `VersatileImageField` with PNG, GIF and JPEG files; the list above is what PIL supports, for more information about per filetype support in PIL [visit here](https://infohost.nmt.edu/tcc/help/pubs/pil/formats.html).

### Registering Sizers & Filters for use on `VersatileImageField` ###

Registering Sizers and Filters is easy and straight-forward; if you've ever registered a model with django's `admin` you'll feel right at home.

It is recommended you write any custom Sizers & Filters within a module named `versatileimagefield` (i.e. `versatileimagefield.py`) that is available at the 'top level' of an app on `INSTALLED_APPS`. Here's an example:

```
somedjangoapp/
    models.py               # Models
    admin.py                # Admin config
    versatilimagefield.py   # Custom Sizers & Filters here
```

After defining your Sizers & Filters you'll need to register them with the `versatileimagefield_registry`. Here's how the `ThumbnailSizer` is registered (see the bottom of the code block for the relevant bit):

```python
import StringIO

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
        Returns a StringIO instance of `image` that will fit
        within a bounding box as specified by `width`x`height`
        """
        imagefile = StringIO.StringIO()
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
versatileimagefield_registry.register_sizer('thumbnail', ThumbnailImage)]
```

All Sizers are registered via the `versatileimagefield_registry.register_sizer` method. The first argument is the attribute you want to make the Sizer available at and the second is the SizedImage subclass.

Filters are just as easy. Here's how the `InvertImage` filter is registered (see the bottom of this code block for the relevant bit):

```python
import StringIO

from PIL import ImageOps

from .datastructures import FilteredImage
from .registry import versatileimagefield_registry


class InvertImage(FilteredImage):
    """
    Inverts the colors of an image.

    See the `process_image()` for more specifics
    """

    filename_key = 'invert'

    def process_image(self, image, image_format, save_kwargs={}):
        """
        Returns a StringIO instance of `image` with inverted colors
        """
        imagefile = StringIO.StringIO()
        inv_image = ImageOps.invert(image)
        inv_image.save(
            imagefile,
            **save_kwargs
        )
        return imagefile

versatileimagefield_registry.register_filter('invert', InvertImage)
```

All Filters are registered via the `versatileimagefield_registry.register_filter` method. The first argument is the attribute you want to make the Filter available at and the second is the FilteredImage subclass.

##### Overriding an existing Sizer or Filter #####

If you try to register a Sizer or Filter with an attribute name that's already in use (like `crop` or `thumbnail` or `invert`), an `AlreadyRegistered` exception will raise.

> ###### NOTE ######
> A Sizer can have the same name as a Filter (since names are only required to be unique per type) however it's not recommended.

If you'd like to override an already-registered Sizer or Filter just use either the `unregister_sizer` or `unregister_filter` methods of `versatileimagefield_registry`. Here's how you could 'override' the `crop` Sizer:

```python
from versatileimagefield.registry import versatileimagefield_registry

# Unregistering the 'crop' Sizer
versatileimagefield_registry.unregister_sizer('crop')
# Registering a custom 'crop' Sizer
versatileimagefield_registry.register_sizer('crop', SomeCustomSizedImageCls)
```

The order that Sizers and Filters register corresponds to their containing app's position on `INSTALLED_APPS`. This means that if you want to override one of the default Sizers or Filters your app needs to be included after `'versatileimagefield'`:

```python
# settings.py
INSTALLED_APPS = (
    'versatileimagefield',
    'yourcustomapp'  # This app can override the default Sizers & Filters
)
```

###### Unallowed Sizer & Filter Names ######

Sizer and Filter names cannot begin with an underscore as it would prevent them from being accessible within the template layer. Additionally, since Sizers are available for use directly on a `VersatileImageField`, there are some Sizer names that are unallowed; trying to register a Sizer with one of the following names will result in a `UnallowedSizerName` exception:

* `build_filters_and_sizers`
* `chunks`
* `close`
* `closed`
* `delete`
* `encoding`
* `field`
* `file`
* `fileno`
* `filters`
* `flush`
* `height`
* `instance`
* `isatty`
* `multiple_chunks`
* `name`
* `newlines`
* `open`
* `path`
* `ppoi`
* `read`
* `readinto`
* `readline`
* `readlines`
* `save`
* `seek`
* `size`
* `softspace`
* `storage`
* `tell`
* `truncate`
* `url`
* `validate_ppoi`
* `width`
* `write`
* `writelines`
* `xreadlines'

## Specifying a Primary Point of Interest (PPOI) ##

The `crop` Sizer is super-useful for creating images at a specific size/aspect-ratio however, sometimes you want the 'crop centerpoint' to be somewhere other than the center of a particular image. In fact, the initial inspiration for `django-versatileimagefield` came as a result of tackling this very problem.

PIL's [`ImageOps.fit`](http://pillow.readthedocs.org/en/latest/reference/ImageOps.html#PIL.ImageOps.fit) method (by [Kevin Cazabon](http://www.cazabon.com/)) is what powers the image manipulation of `crop` Sizer and it takes an optional keyword argument, `centering`, which expects a 2-tuple comprised of floats which are less than 0 and greater than 1. These two values together form a cartesian-like coordinate system that dictates where to center the crop (examples: `(0, 0)` will crop to the top left corner, `(0.5, 0.5)` will crop to the center and `(1, 1)` will crop to the bottom right corner).

> ### NOTE ###
> At present, only the `crop` Sizer leverages PPOI to while creating images but a `VersatileImageField` makes its PPOI value available to ALL its attached Filters and Sizers. Get creative!

### The PPOIField ###

Each image managed by a `VersatileImageField` can store its own, unique PPOI in the database via the easy-to-use `PPOIField`. Here's what it looks like in action on our example model:

```python
# models.py with `VersatileImageField` & `PPOIField`
from django.db import models

from versatileimagefield.fields import VersatileImageField, \
    PPOIField

class ImageExampleModel(models.Model):
    name = models.CharField(
        'Name',
        max_length=80
    )
    image = VersatileImageField(
        'Image',
        upload_to='images/testimagemodel/',
        width_field='width',
        height_field='height',
        ppoi_field='ppoi'
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )
    ppoi = PPOIField(
        'Image PPOI'
    )

    class Meta:
        verbose_name = 'Image Example'
        verbose_name_plural = 'Image Examples'
```

As you can see, you'll need to add a new `PPOIField` field to your model and then include the name of that field in the `VersatileImageField`'s `ppoi_field` keyword argument. That's it!

> #### NOTE ####
> `PPOIField` is fully-compatible with [`south`](http://south.readthedocs.org/en/latest/index.html) so migrate to your heart's content!

#### How PPOI is Stored in the Database ####

The **Primary Point of Interest** is stored in the database as a string with the x and y coordinates limited to two decimal places and separated by an 'x' (for instance: `'0.5x0.5'` or `0.62x0.28`).

### Setting your PPOI ###

You should **always** set an image's PPOI directly on a `VersatileImageField` (as opposed to directly on a `PPOIField` attribute).

> #### NOTE ####
> On save, `VersatileImageField` will ensure its currently-assigned PPOI value is 'sent' to the `PPOIField` associated with it (if any) prior to writing to the database.

#### Via The Shell ####

```python
# Importing our example Model
>>> from someapp.models import ImageExampleModel
# Retrieving a model instance
>>> example = ImageExampleModel.objects.all()[0]
# Retrieving the current PPOI value associated with the image field
# A `VersatileImageField`'s PPOI value is ALWAYS associated with the `ppoi`
# attribute, irregardless of what you named the `PPOIField` attribute on your model
>>> example.image.ppoi
(0.5, 0.5)
# Creating a cropped image
>>> example.image.crop['400x400'].url
u'/media/__sized__/images/testimagemodel/test-image-crop-c0-5__0-5-400x400.jpg'
# Changing the PPOI value
>>> example.image.ppoi = (1, 1)
# Creating a new cropped image with the new PPOI value
>>> example.image.crop['400x400'].url
u'/media/__sized__/images/testimagemodel/test-image-crop-c1__1-400x400.jpg'
# PPOI values can be set as either a tuple or a string
>>> example.image.ppoi = '0.1x0.55'
>>> example.image.ppoi
(0.1, 0.55)
>>> example.image.ppoi = (0.75, 0.25)
>>> example.image.crop['400x400'].url
u'/media/__sized__/images/testimagemodel/test-image-crop-c0-75__0-25-400x400.jpg'
# u'0.75x0.25' is written to the database in the 'ppoi' column associated with
# our example model
>>> example.save()
```

As you can see, changing an image's PPOI changes the filename of the cropped image. This ensures updates to a `VersatileImageField`'s PPOI value will result in unique cache entries for each unique image it creates.

> ##### NOTE #####
> Each time a field's PPOI is set, its attached Filters & Sizers will be immediately updated with the new value.

#### Via The Admin ####

It's pretty hard to accurately set a particular image's PPOI when working in the Python shell so `django-versatileimagefield` ships with an admin-ready formfield. Simply add an image, click 'Save and continue editing', and then click where you'd like the PPOI to be. A helpful translucent red square will indicate where the PPOI value is currently set to on the image:

![django-versatileimagefield PPOI admin widget example](versatileimagefield/static/versatileimagefield/images/ppoi-admin-example.png)

# TODO
* Placeholder docs
