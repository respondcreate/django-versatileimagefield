# django-versatileimagefield #

## About ##

A drop-in replacement for django's ImageField that provides an easily-extendable sizing and filters framework for your images.

### Current Version ###

0.1

## Installation ##

Installation is easy with [pip](https://pypi.python.org/pypi/pip):

```bash
$ pip install django-versatileimagefield
```

### Dependencies ###

* `Pillow` >= 2.4.0

`django-versatileimagefield` depends on the excellent [`Pillow`](http://pillow.readthedocs.org) library. If you already have PIL installed, it is recommended you uninstall PIL prior to installing `django-versatileimagefield`:

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
    # Defaults to 'versatileimagefield_cache'. If no cache exists to the name
    # provided, the 'default' cache will be used.
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
    # The name of the top-level folder within your storage to save all
    # sized images. Defaults to '__sized__'
    'sized_directory_name': '__sized__',
    # The name of the directory to save all filtered images within.
    # Defaults to '__filtered__':
    'filtered_directory_name': '__filtered__'
}
```

## Overview ##

`django-versatileimagefield` gives you a simple interface for creating new images from a single image.

### Model Example ###

It works just like django's `ImageField` and can be used as a drop-in replacement. Here's a simple model that uses django's `ImageField`:

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
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
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
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
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

Where VersatileImageField shines is in its ability to create new images on the fly via the 'Sizer/Filter' framework.

### Sizers ###

The Sizer framework gives you a way to create images with sizes different from the one you uploaded to the field. `VersatileImageField` ships with two sizers, `thumbnail` and `crop`.

#### thumbnail ####

Let's say you wanted to create a thumbnail of an image that would fit within a 400px by 400px bounding box:

```python
>>> from someapp.models import ImageExampleModel
>>> example = ImageExampleModel.objects.all()[0]
>>> example.image.name
u'images/testimagemodel/test-image.jpg'
>>> example.image.thumbnail['400x400']
u'/media/__sized__/images/testimagemodel/test-image-thumbnail-400x400.jpg'
```

#### crop ####

If you wanted make an image cropped to a specific size, use the 'crop' sizer:

```python
>>> from someapp.models import ImageExampleModel
>>> example = ImageExampleModel.objects.all()[0]
>>> example.image.name
u'images/testimagemodel/test-image.jpg'
>>> example.image.crop['400x400']
u'/media/__sized__/images/testimagemodel/test-image-crop-c0-5__0-5-400x400.jpg'
```

> ### NOTE ###
> The `crop` sizer will scale an image down to its longest side and then crop inwards, centered on the **primary point of interest** (ppoi). For more info about PPOI see the _Specifying a Primary Point of Interest (PPOI)_ heading below.

As you can see, `VersatileImageField` has two extra attributes – 'thumbnail' and 'crop' – which are just `dict` subclasses that expect keys comprised of two integers, representing width and height respectively, separated by an 'x'.

#### How Sized Files are Named/Stored ####

All Sizers subclass from `versatileimagefield.datastructures.sizedimage.SizedImage` which provides a get_filename_key method that provides a unique-to-size-specified string which is included in the filename of each image it creates. The `thumbnail` sizer simply combines '-thumbnail-' with the size key passed (i.e. '400x400' ) while the `crop` sizer combines '-crop-', the field's ppoi value as a string and the size key.

All images created by a Sizer are stored within the field's `storage` class in a top-level folder named '__sized__', maintaining the same folder structure as the original image. If you'd like to change the name of this folder to something other than '__sized__', adjust the value of VERSATILEIMAGEFIELD_SETTINGS['sized_directory_name'] within your settings file.

Sizers are quick and easy to write, for more information about creating your own, see the 'Writing Custom Sizers' section below.

### Filters ###

Filters are similar to Sizers in that they create new images but they differ in a few key ways. An example by way of our `TestImageModel` model:

```python
>>> from someapp.models import ImageExampleModel
>>> example = ImageExampleModel.objects.all()[0]
>>> example.image.name
u'images/testimagemodel/test-image.jpg'
>>> example.image.filters.invert.name
u'images/testimagemodel/__filtered__/test-image__invert__.jpg'
>>> example.image.filters.invert.url
```

As you can see, there's a 'filters' attribute available on the image field which contains all filters currently registered to the Filter registry (more on that in a minute).

> #### NOTE ####
> `django-versatileimagefield` ships with only a single Filter – 'invert' – which inverts the colors of an image.

What makes Filters extra-useful is that they have access to all Sizers:

```python
>>> example.image.filters.invert.thumbnail['400x400']
u'/media/images/testimagemodel/__filtered__/test-image__invert__-thumbnail-400x400.jpg'
>>> example.image.filters.invert.crop['400x400']
u'/media/images/testimagemodel/__filtered__/test-image__invert__-c0-5__0-5-400x400.jpg'
```

> #### When Filtered Images Are Created ####
> Images are created by a Filter when that filter is accessed for the first time on each `VersatileImageField`. Once created, a reference is stored in the cache for speedy subsequent retrievals.

Filters are quick and easy to write, for more information about creating your own, see the 'Writing Custom Filters' section below.

## Accessing Sizers / Filters in Templates ##

Template usage is straight forward and easy since both attributes and dictionary keys can be accessed via dot-notation; no crufty templatetags necessary:

```html
<!-- Sizers -->
<img src="{{ image.thumbnail.400x400 }}" />
<img src="{{ image.crop.400x400 }}" />

<!-- Filters -->
<img src="{{ image.filters.invert.url }}" />

<!-- Filters + Sizers -->
<img src="{{ image.filters.invert.thumbnail.400x400 }}" />
<img src="{{ image.filters.invert.crop.400x400 }}" />
```

## Specifying a Primary Point of Interest (PPOI) ##

The 'crop' Sizer is SUPER useful for creating images at a specific size/aspect-ratio however, sometimes you want the 'crop centerpoint' to be somewhere other than the center of a particular image. In fact, the initial inspiration for `django-versatileimagefield` came as a result of tackling this very problem.

PIL's [`ImageOps.fit`](http://pillow.readthedocs.org/en/latest/reference/ImageOps.html#PIL.ImageOps.fit) method (by [Kevin Cazabon](http://www.cazabon.com/)) is what powers the 'crop' Sizer and it takes an optional keyword argument, `centering`, which expects a 2-tuple comprised of floats which are `>= 0` & `<= 1`. These two values together form a cartesian-like coordinate system that dictates where to center the crop: `(0, 0)` will crop to the top left corner, `(0.5, 0.5)` will crop to the center and `(1, 1)` will crop to the bottom right corner.

### The PPOIField ###

Each image managed by a `VersatileImageField` can store its own, unique PPOI in the database via the `PPOIField`. Here's what it looks like in action on our example model:

```python
# models.py with `VersatileImageField`
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
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    ppoi = PPOIField()

    class Meta:
        verbose_name = 'Image Example'
        verbose_name_plural = 'Image Examples'
```

As you can see, you'll need to add a new PPOIField field to your model and then include the name of that field in the `VersatileImageField`'s `ppoi_field` keyword argument. That's it!

> #### NOTE ####
> `PPOIField` is fully-compatible with [`south`](http://south.readthedocs.org/en/latest/index.html) so migrate to your heart's content!

#### How PPOI is Stored in the Database ####

The Primary Point of Interest is stored in the database as a string with the x and y coordinates limited to two decimal places and separated by an 'x', e.g. `'0.5x0.5'`.

### Setting your PPOI ###

You should always set ppoi directly on a `VersatileImageField` attribute (as opposed to on a `PPOIField` attribute).

#### Via The Shell ####

```python
>>> from someapp.models import ImageExampleModel
>>> example = ImageExampleModel.objects.all()[0]
>>> example.image.ppoi
(0.5, 0.5)
>>> example.image.crop['400x400']
u'/media/__sized__/images/testimagemodel/test-image-crop-c0-5__0-5-400x400.jpg'
>>> example.image.ppoi = (1, 1)
>>> example.image.crop['400x400']
u'/media/__sized__/images/testimagemodel/test-image-crop-c1__1-400x400.jpg'
>>> example.image.ppoi = (0.75, 0.25)
>>> example.image.crop['400x400']
u'/media/__sized__/images/testimagemodel/test-image-crop-c0-75__0-25-400x400.jpg'
```

As you can see, changing an image's PPOI changes the filename of the cropped image.

> ##### NOTE #####
> Each time a field's PPOI is set it's Filters & Sizers will be immediately re-built to account for this change.

#### Via The Admin ####

It's pretty hard to accurately set a particular image's PPOI when working in the Python shell so `django-versatileimagefield` ships with an admin-ready formfield. Simply add an image, click 'Save and continue editing', and then click where you'd like the PPOI to be, a helpful translucent red square will show you where it is:

![django-versatileimagefield PPOI admin widget example](versatileimagefield/static/versatileimagefield/images/ppoi-admin-example.png)

# TODO
* Add 'Writing Custom Sizers' section to README
* Add 'Writing Custom Filters' section to README
