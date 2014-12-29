from django.db import models
from versatileimagefield.fields import VersatileImageField, PPOIField


class VersatileImageTestModel(models.Model):
    """A model for testing VersatileImageFields"""
    img_type = models.CharField(
        max_length=5,
        unique=True
    )
    image = VersatileImageField(
        upload_to='/',
        ppoi_field='ppoi'
    )
    optional_image = VersatileImageField(
        upload_to='optional/',
        blank=True
    )
    ppoi = PPOIField()
