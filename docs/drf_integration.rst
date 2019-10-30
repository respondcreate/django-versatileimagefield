Django REST Framework Integration
=================================

If you've got an API powered by `Tom Christie <https://twitter.com/_tomchristie>`_'s excellent `Django REST Framework <http://www.django-rest-framework.org/>`_ and want to serve images in multiple sizes/renditions ``django-versatileimagefield`` has you covered with its  ``VersatileImageFieldSerializer``.

.. _example-model:

Example
-------

To demonstrate how it works we'll use this simple model:

.. code-block:: python

    # myproject/person/models.py

    from django.db import models

    from versatileimagefield.fields import VersatileImageField, PPOIField


    class Person(models.Model):
        """Represents a person."""
        name_first = models.CharField('First Name', max_length=80)
        name_last = models.CharField('Last Name', max_length=100)
        headshot = VersatileImageField(
            'Headshot',
            upload_to='headshots/',
            ppoi_field='headshot_ppoi'
        )
        headshot_ppoi = PPOIField()

        class Meta:
            verbose_name = 'Person'
            verbose_name_plural = 'People'

.. _serialization:

OK, let's write a simple ``ModelSerializer`` subclass to serialize Person instances:

.. code-block:: python
    :emphasize-lines: 5,12-19

    # myproject/person/serializers.py

    from rest_framework import serializers

    from versatileimagefield.serializers import VersatileImageFieldSerializer

    from .models import Person


    class PersonSerializer(serializers.ModelSerializer):
        """Serializes Person instances"""
        headshot = VersatileImageFieldSerializer(
            sizes=[
                ('full_size', 'url'),
                ('thumbnail', 'thumbnail__100x100'),
                ('medium_square_crop', 'crop__400x400'),
                ('small_square_crop', 'crop__50x50')
            ]
        )

        class Meta:
            model = Person
            fields = (
                'name_first',
                'name_last',
                'headshot'
            )

And here's what it would look like serialized:

.. code-block:: python
    :emphasize-lines: 14-19

    >>> from myproject.person.models import Person
    >>> john_doe = Person.objects.create(
    ...     name_first='John',
    ...     name_last='Doe',
    ...     headshot='headshots/john_doe_headshot.jpg'
    ... )
    >>> john_doe.save()
    >>> from myproject.person.serializers import PersonSerializer
    >>> john_doe_serialized = PersonSerializer(john_doe)
    >>> john_doe_serialized.data
    {
        'name_first': 'John',
        'name_last': 'Doe',
        'headshot': {
            'full_size': 'http://api.yoursite.com/media/headshots/john_doe_headshot.jpg',
            'thumbnail': 'http://api.yoursite.com/media/headshots/john_doe_headshot-thumbnail-400x400.jpg',
            'medium_square_crop': 'http://api.yoursite.com/media/headshots/john_doe_headshot-crop-c0-5__0-5-400x400.jpg',
            'small_square_crop': 'http://api.yoursite.com/media/headshots/john_doe_headshot-crop-c0-5__0-5-50x50.jpg',
        }
    }

As you can see, the ``sizes`` argument on ``VersatileImageFieldSerializer`` simply unpacks the list of 2-tuples using the value in the first position as the attribute of the image and the second position as a 'Rendition Key' which dictates how the original image should be modified.

.. _reusing-rendition-key-sets:

Reusing Rendition Key Sets
~~~~~~~~~~~~~~~~~~~~~~~~~~

It's common to want to re-use similar sets of images across models and fields so ``django-versatileimagefield`` provides a setting, ``VERSATILEIMAGEFIELD_RENDITION_KEY_SETS`` for defining them (:ref:`docs <rendition-key-sets>`).

Let's move the Rendition Key Set we used above into our settings file:

.. code-block:: python

    # myproject/settings.py

    VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
        'person_headshot': [
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
            ('medium_square_crop', 'crop__400x400'),
            ('small_square_crop', 'crop__50x50')
        ]
    }

Now, let's update our serializer to use it:

.. code-block:: python
    :emphasize-lines: 13

    # myproject/person/serializers.py

    from rest_framework import serializers

    from versatileimagefield.serializers import VersatileImageFieldSerializer

    from .models import Person


    class PersonSerializer(serializers.ModelSerializer):
        """Serializes Person instances"""
        headshot = VersatileImageFieldSerializer(
            sizes='person_headshot'
        )

        class Meta:
            model = Person
            fields = (
                'name_first',
                'name_last',
                'headshot'
            )

That's it! Now that you know how to define Rendition Key Sets, leverage them to :doc:`improve performance </improving_performance>`!
