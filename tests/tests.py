import os
from shutil import rmtree

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import Client, TestCase

from versatileimagefield.image_warmer import VersatileImageFieldWarmer
from versatileimagefield.settings import VERSATILEIMAGEFIELD_SIZED_DIRNAME,\
    VERSATILEIMAGEFIELD_FILTERED_DIRNAME

from .models import VersatileImageTestModel
from .serializers import VersatileImageTestModelSerializer


class VersatileImageFieldTestCase(TestCase):
    fixtures = ['versatileimagefield']

    def setUp(self):
        self.jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        self.png = VersatileImageTestModel.objects.get(img_type='png')
        self.gif = VersatileImageTestModel.objects.get(img_type='gif')
        password = '12345'
        user = User.objects.create_user(
            username='test',
            email='test@test.com',
            password=password
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        client = Client()
        login = client.login(
            username='test',
            password=password
        )
        self.assertTrue(login)
        self.user = user
        self.client = client

    def tearDown(self):
        """
        Deletes files made by VersatileImageFields during tests
        """
        filtered_path = os.path.join(
            settings.MEDIA_ROOT,
            VERSATILEIMAGEFIELD_FILTERED_DIRNAME
        )
        sized_path = os.path.join(
            settings.MEDIA_ROOT,
            VERSATILEIMAGEFIELD_SIZED_DIRNAME
        )
        rmtree(filtered_path, ignore_errors=True)
        rmtree(sized_path, ignore_errors=True)

    @staticmethod
    def bad_ppoi(versatileimagefield):
        """
        Accepts a VersatileImageFieldFile instance and attempts to
        assign a bad PPOI value to it. Should raise a ValidationError
        """
        versatileimagefield.ppoi = (1.5, 2)

    def test_check_storage_paths(self):
        """Ensure storage paths are properly set"""
        self.assertEqual(self.jpg.image.name, 'python-logo.jpg')
        self.assertEqual(self.png.image.name, 'python-logo.png')
        self.assertEqual(self.gif.image.name, 'python-logo.gif')

    def test_thumbnail_resized_path(self):
        """Ensure thumbnail Sizer paths are set correctly"""
        self.assertEqual(
            self.jpg.image.thumbnail['100x100'].url,
            '/media/__sized__/python-logo-thumbnail-100x100.jpg'
        )

    def test_crop_resized_path(self):
        """Ensure crop Sizer paths are set correctly"""
        self.assertEqual(
            self.jpg.image.crop['100x100'].url,
            '/media/__sized__/python-logo-crop-c0-25__0-25-100x100.jpg'
        )
        self.assertEqual(
            self.gif.image.crop['100x100'].url,
            '/media/__sized__/python-logo-crop-c0-75__0-75-100x100.gif'
        )
        self.assertEqual(
            self.png.image.crop['100x100'].url,
            '/media/__sized__/python-logo-crop-c0-5__0-5-100x100.png'
        )

    def test_invert_filtered_path(self):
        """Ensure crop Sizer paths are set correctly"""
        self.assertEqual(
            self.jpg.image.filters.invert.url,
            '/media/__filtered__/python-logo__invert__.jpg'
        )

    def test_invert_plus_thumbnail_sizer_filtered_path(self):
        """Ensure crop Sizer paths are set correctly"""
        self.assertEqual(
            self.jpg.image.filters.invert.thumbnail['100x100'].url,
            (
                '/media/__sized__/__filtered__/python-logo__invert__'
                '-thumbnail-100x100.jpg'
            )
        )

    def test_setting_ppoi_values(self):
        """Ensure PPOI values are set correctly"""
        jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        self.assertEqual(
            jpg.image.ppoi,
            (0.25, 0.25)
        )
        jpg.image.ppoi = (0.5, 0.5)
        jpg.save()
        self.assertEqual(
            jpg.image.ppoi,
            (0.5, 0.5)
        )
        jpg.image.ppoi = '(0.77, 0.77)'
        jpg.save()
        jpg.image.ppoi = '0.25x0.25'
        jpg.save()
        self.assertEqual(
            jpg.image.ppoi,
            (0.25, 0.25)
        )
        self.assertRaises(ValidationError, self.bad_ppoi(jpg.image))

    def test_create_on_demand_boolean(self):
        """Ensure create_on_demand boolean is set appropriately"""
        jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        self.assertFalse(jpg.image.create_on_demand)
        jpg.image.create_on_demand = True
        self.assertTrue(jpg.image.create_on_demand)

    def test_create_on_demand_functionality(self):
        """Ensures create_on_demand functionality works as advertised"""
        jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        img_url = jpg.image.crop['100x100'].url
        self.assertEqual(
            cache.get(img_url),
            None
        )
        jpg.image.create_on_demand = True
        jpg.image.crop['100x100'].url
        self.assertEqual(
            cache.get(img_url),
            1
        )
        self.assertTrue(
            jpg.image.field.storage.exists(jpg.image.crop['100x100'].name)
        )
        jpg.image.field.storage.delete(jpg.image.crop['100x100'].name)
        self.assertFalse(
            jpg.image.field.storage.exists(jpg.image.crop['100x100'].name)
        )
        cache.delete(img_url)
        self.assertEqual(
            cache.get(img_url),
            None
        )

    def test_image_warmer(self):
        """Ensures VersatileImageFieldWarmer works as advertised."""
        jpg_warmer = VersatileImageFieldWarmer(
            instance_or_queryset=self.jpg,
            rendition_key_set='test_set',
            image_attr='image'
        )
        num_created, failed_to_create = jpg_warmer.warm()
        self.assertEqual(num_created, 5)
        all_imgs_warmer = VersatileImageFieldWarmer(
            instance_or_queryset=VersatileImageTestModel.objects.all(),
            rendition_key_set=(
                ('test_thumb', 'thumbnail__100x100'),
            ),
            image_attr='image',
            verbose=True
        )
        num_created, failed_to_create = all_imgs_warmer.warm()

    def test_VersatileImageFieldSerializer_output(self):
        """Ensures VersatileImageFieldSerializer serializes correctly"""
        serializer = VersatileImageTestModelSerializer(self.jpg)
        self.assertEqual(
            serializer.data.get('image'),
            {
                'test_crop': (
                    '/media/__sized__/python-logo-crop-c0-25__'
                    '0-25-100x100.jpg'
                ),
                'test_invert_crop': (
                    '/media/__sized__/__filtered__/python-logo__'
                    'invert__-crop-c0-25__0-25-100x100.jpg'
                ),
                'test_invert_thumb': (
                    '/media/__sized__/__filtered__/python-logo__'
                    'invert__-thumbnail-100x100.jpg'
                ),
                'test_invert': '/media/python-logo.jpg',
                'test_thumb': (
                    '/media/__sized__/python-logo-thumbnail'
                    '-100x100.jpg'
                )
            }
        )

    def test_widget_javascript(self):
        """
        Ensures the VersatileImagePPOIClickWidget widget loads appropriately
        and its image preview is available
        """
        response = self.client.get('/admin/tests/versatileimagetestmodel/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            (
                '<img src="/media/__sized__/python-logo-thumbnail-300x300.png"'
                ' id="image_0_imagepreview" data-hidden_field_id="id_image_1"'
                ' data-point_stage_id="image_0_point-stage" '
                'data-ppoi_id="image_0_ppoi" class="sizedimage-preview"/>'
                in response.content
            )
        )
        self.assertTrue(
            (
                '<script type="text/javascript" src="/static/'
                'versatileimagefield/js/versatileimagefield.js"></script>'
                in response.content
            )
        )
        self.assertTrue(
            self.png.image.field.storage.exists(
                self.png.image.thumbnail['300x300'].name
            )
        )

    def test_VersatileImageFieldDescriptor__set__(self):
        """
        Ensures VersatileImageFieldDescriptor.__set__ works as intended
        """
        self.jpg.image = 'python-logo-2.jpg'
        self.jpg.save()
        self.assertEqual(
            self.jpg.image.thumbnail['100x100'].url,
            '/media/__sized__/python-logo-2-thumbnail-100x100.jpg'
        )
        self.jpg.image = 'python-logo.jpg'
        self.jpg.save()
        self.assertEqual(
            self.jpg.image.thumbnail['100x100'].url,
            '/media/__sized__/python-logo-thumbnail-100x100.jpg'
        )
