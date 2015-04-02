import os

from django.db import models

from versatileimagefield.fields import VersatileImageField, PPOIField
from versatileimagefield.placeholder import (
    OnDiscPlaceholderImage,
    OnStoragePlaceholderImage
)


class VersatileImageTestModel(models.Model):
    """A model for testing VersatileImageFields"""
    img_type = models.CharField(
        max_length=5,
        unique=True
    )
    image = VersatileImageField(
        upload_to='./',
        ppoi_field='ppoi',
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
    optional_image = VersatileImageField(
        upload_to='./',
        blank=True,
        placeholder_image=OnDiscPlaceholderImage(
            path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'placeholder.gif'
            )
        )
    )
    optional_image_2 = VersatileImageField(
        upload_to='./',
        blank=True,
        placeholder_image=OnStoragePlaceholderImage(
            path='on-storage-placeholder/placeholder.gif'
        )
    )
    optional_image_3 = VersatileImageField(
        upload_to='./',
        blank=True
    )
    ppoi = PPOIField()
