from rest_framework.serializers import ModelSerializer

from versatileimagefield.serializers import VersatileImageFieldSerializer

from .models import VersatileImageTestModel


class VersatileImageTestModelSerializer(ModelSerializer):
    """Serializes VersatileImageTestModel instances"""
    image = VersatileImageFieldSerializer(
        sizes='test_set'
    )

    class Meta:
        model = VersatileImageTestModel
        fields = (
            'image',
        )
