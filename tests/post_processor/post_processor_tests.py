from .models import VersatileImagePostProcessorTestModel
from ..tests import VersatileImageFieldBaseTestCase


class VersatileImageFieldPostProcessorTestCase(
    VersatileImageFieldBaseTestCase
):
    fixtures = ['post_processor']

    def test_post_processor(self):
        """
        Ensure versatileimagefield.registry.autodiscover raises the
        appropriate exception when trying to import on versatileimage.py
        modules.
        """
        instance, created = VersatileImagePostProcessorTestModel.\
            objects.get_or_create(pk=1)
        self.assertEqual(
            instance.optional_image.crop['100x100'].url,
            '/media/__sized__/__placeholder__/on-storage-placeholder/'
            'placeholder-c3d14a7758159677.png'
        )
