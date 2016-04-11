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
        instance = VersatileImagePostProcessorTestModel.objects.get(pk=1)
        instance.create_on_demand = True
        self.assertEqual(
            instance.image.crop['100x100'].url,
            '/media/__sized__/python-logo-2c88a725748e22ee.jpg'
        )

    def test_obscured_file_delete(self):
        instance = VersatileImagePostProcessorTestModel.objects.get(pk=1)
        self.assert_VersatileImageField_deleted(instance.image)
