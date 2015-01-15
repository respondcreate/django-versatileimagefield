import os

from django.db import models
from django.core.files.base import ContentFile

from versatileimagefield.fields import VersatileImageField, PPOIField

placeholder_image = open(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'placeholder.gif'
    ), 'r'
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
    )
    optional_image = VersatileImageField(
        upload_to='./',
        blank=True,
        placeholder_image=ContentFile(placeholder_image.read(), name='placeholder.gif')
    )
    optional_image_2 = VersatileImageField(
        upload_to='./',
        blank=True
    )
    ppoi = PPOIField()
