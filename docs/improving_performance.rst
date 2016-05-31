Improving Performance
=====================

During development, ``VersatileImageField``'s :ref:`on-demand image creation <on-demand-image-creation>` enables you to quickly iterate but, once your application is deployed into production, this convenience adds a small bit of overhead that you'll probably want to turn off.

Turning off on-demand image creation
------------------------------------

To turn off on-demand image creation just set the ``'create_images_on_demand'`` key of the ``VERSATILEIMAGEFIELD_SETTINGS`` setting to ``False`` (:ref:`docs <versatileimagefield-settings>`). Now your ``VersatileImageField`` fields will return URLs to images without first checking to see if they've actually been created yet.

.. note:: Once an image has been created by a ``VersatileImageField``, a reference to it is stored in the cache which makes for speedy subsequent retrievals. Setting ``VERSATILEIMAGEFIELD_SETTINGS['create_images_on_demand']`` to ``False`` bypasses this entirely making ``VersatileImageField`` perform even faster (:ref:`docs <versatileimagefield-settings>`).

Ensuring images are created
---------------------------

This boost in performance is great but now you'll need to ensure that the images your application links-to actually exist. Luckily, ``VersatileImageFieldWarmer`` will help you do just that. Here's an example in the Python shell using the :ref:`example model <example-model>` from the Django REST Framework serialization example:

.. code-block:: python

    >>> from myproject.person.models import Person
    >>> from versatileimagefield.image_warmer import VersatileImageFieldWarmer
    >>> person_img_warmer = VersatileImageFieldWarmer(
    ...     instance_or_queryset=Person.objects.all(),
    ...     rendition_key_set='person_headshot',
    ...     image_attr='headshot',
    ...     verbose=True
    ... )
    >>> num_created, failed_to_create = person_img_warmer.warm()

``num_created`` will be an integer of how many images were successfully created and ``failed_to_create`` will be a list of paths to images (on the field's storage class) that could not be created (due to a `PIL/Pillow <https://pillow.readthedocs.io/>`_ error, for example).

This technique is useful if you've recently converted your project's ``models.ImageField`` fields to use ``VersatileImageField`` or if you want to 'pre warm' images as part of a `Fabric <http://www.fabfile.org/>`_ script.

.. note:: The above example would create a set of images (as dictated by the ``'person_headshot'`` :ref:`Rendition Key Set <reusing-rendition-key-sets>`) for the ``headshot`` field of each ``Person`` instance. ``rendition_key_set`` also accepts a valid :ref:`Rendition Key Set <rendition-key-sets>` directly:

    .. code-block:: python
        :emphasize-lines: 3-6

        >>> person_img_warmer = VersatileImageFieldWarmer(
        ...     instance_or_queryset=Person.objects.all(),
        ...     rendition_key_set=[
        ...         ('large_horiz_crop', '1200x600'),
        ...         ('large_vert_crop', '600x1200'),
        ...     ],
        ...     image_attr='headshot',
        ...     verbose=True
        ... )

.. note:: Setting ``verbose=True`` when instantiating a ``VersatileImageFieldWarmer`` will display a yum-style progress bar showing the image warming progress:

    .. code-block:: python

        >>> num_created, failed_to_create = person_img_warmer.warm()
        [###########----------------------------------------] 20/100 (20%)

.. note:: The ``image_attr`` argument can be dot-notated in order to follow ``ForeignKey`` and ``OneToOneField`` relationships. Example: ``'related_model.headshot'``.

Auto-creating sets of images on ``post_save``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You also might want to create new images immediately after model instances are saved. Here's how we'd do it with our example model (see highlighted lines below):

.. code-block:: python
    :emphasize-lines: 4,7,25-33

    # myproject/person/models.py

    from django.db import models
    from django.dispatch import receiver

    from versatileimagefield.fields import VersatileImageField, PPOIField
    from versatileimagefield.image_warmer import VersatileImageFieldWarmer


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

    @receiver(models.signals.post_save, sender=Person)
    def warm_Person_headshot_images(sender, instance, **kwargs):
        """Ensures Person head shots are created post-save"""
        person_img_warmer = VersatileImageFieldWarmer(
            instance_or_queryset=instance,
            rendition_key_set='person_headshot',
            image_attr='headshot'
        )
        num_created, failed_to_create = person_img_warmer.warm()
