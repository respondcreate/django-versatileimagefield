from __future__ import division
from __future__ import unicode_literals

from functools import reduce
import math
import operator
import os
from shutil import rmtree

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import serializers
from django.template import Context
from django.template.loader import get_template
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.utils._os import upath
from django.utils.six.moves import cPickle as pickle

from PIL import Image
from versatileimagefield.files import VersatileImageFileDescriptor
from versatileimagefield.datastructures.filteredimage import InvalidFilter
from versatileimagefield.datastructures.sizedimage import \
    MalformedSizedImageKey, SizedImage
from versatileimagefield.datastructures.filteredimage import FilteredImage
from versatileimagefield.image_warmer import VersatileImageFieldWarmer
from versatileimagefield.registry import (
    autodiscover,
    versatileimagefield_registry,
    AlreadyRegistered,
    InvalidSizedImageSubclass,
    InvalidFilteredImageSubclass,
    NotRegistered,
    UnallowedSizerName,
    UnallowedFilterName
)
from versatileimagefield.settings import (
    VERSATILEIMAGEFIELD_SIZED_DIRNAME,
    VERSATILEIMAGEFIELD_FILTERED_DIRNAME,
    VERSATILEIMAGEFIELD_PLACEHOLDER_DIRNAME
)
from versatileimagefield.utils import (
    get_rendition_key_set,
    InvalidSizeKey,
    InvalidSizeKeySet
)
from versatileimagefield.validators import validate_ppoi_tuple
from versatileimagefield.versatileimagefield import CroppedImage, InvertImage

from .forms import VersatileImageTestModelForm
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
        placeholder_path = os.path.join(
            settings.MEDIA_ROOT,
            VERSATILEIMAGEFIELD_PLACEHOLDER_DIRNAME
        )
        rmtree(filtered_path, ignore_errors=True)
        rmtree(sized_path, ignore_errors=True)
        rmtree(placeholder_path, ignore_errors=True)

    @staticmethod
    def imageEqual(image1, image2):
        """
        Returns a bool signifying whether or not `image1` and `image2`
        are identical
        """
        h1 = image1.histogram()
        h2 = image2.histogram()
        rms = math.sqrt(
            reduce(
                operator.add,
                map(lambda a, b: (a - b) ** 2, h1, h2)
            ) // len(h1)
        )
        return rms == 0.0

    @staticmethod
    def bad_ppoi():
        """
        Accepts a VersatileImageFieldFile instance and attempts to
        assign a bad PPOI value to it. Should raise a ValidationError
        """
        versatileimagefield = VersatileImageTestModel.objects.get(
            img_type='jpg'
        ).image
        versatileimagefield.ppoi = (1.5, 2)

    @staticmethod
    def bad_ppoi_2():
        """
        Accepts a VersatileImageFieldFile instance and attempts to
        assign a bad PPOI value to it. Should raise a ValidationError
        """
        versatileimagefield = VersatileImageTestModel.objects.get(
            img_type='jpg'
        ).image
        versatileimagefield.ppoi = 'picklexcucumber'

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

    def invalid_filter_access(self):
        """
        Attempts to access a non-existant filter.
        Should raise InvalidFilter
        """
        invalid_filter = self.jpg.image.filters.non_existant.url
        del invalid_filter

    def test_InvalidFilter(self):
        """Ensure InvalidFilter raises"""
        self.assertRaises(
            InvalidFilter,
            self.invalid_filter_access
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

    def test_placeholder_image(self):
        """Ensures placehold.it integration"""
        self.assertEqual(
            self.jpg.optional_image.crop['100x100'].url,
            '/media/__sized__/__placeholder__/'
            'placeholder-crop-c0-5__0-5-100x100.gif'
        )
        self.assertEqual(
            self.jpg.optional_image.thumbnail['100x100'].url,
            '/media/__sized__/__placeholder__/'
            'placeholder-thumbnail-100x100.gif'
        )
        self.assertEqual(
            self.jpg.optional_image.filters.invert.url,
            '/media/__placeholder__/__filtered__/placeholder__invert__.gif'
        )
        self.assertEqual(
            self.jpg.optional_image_2.crop['100x100'].url,
            '/media/__sized__/__placeholder__/on-storage-placeholder/'
            'placeholder-crop-c0-5__0-5-100x100.gif'
        )
        self.assertEqual(
            self.jpg.optional_image_2.thumbnail['100x100'].url,
            '/media/__sized__/__placeholder__/on-storage-placeholder/'
            'placeholder-thumbnail-100x100.gif'
        )
        self.assertEqual(
            self.jpg.optional_image_2.filters.invert.url,
            '/media/__placeholder__/on-storage-placeholder/__filtered__/'
            'placeholder__invert__.gif'
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
        jpg.image.ppoi = '0.25x0.25'
        jpg.save()
        self.assertEqual(
            jpg.image.ppoi,
            (0.25, 0.25)
        )
        self.assertRaises(ValidationError, self.bad_ppoi)
        self.assertRaises(ValidationError, self.bad_ppoi_2)

    def test_invalid_ppoi_tuple_validation(self):
        """
        Ensure validate_ppoi_tuple works as expected
        """
        self.assertFalse(
            validate_ppoi_tuple((0, 1.5, 6))
        )

    @staticmethod
    def try_invalid_create_on_demand_set():
        """
        Attempts to assign a non-bool value to a VersatileImageField's
        `create_on_demand` attribute
        Should raise ValueError
        """
        jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        jpg.image.create_on_demand = 'pickle'

    def test_create_on_demand_boolean(self):
        """Ensure create_on_demand boolean is set appropriately"""
        jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        self.assertFalse(jpg.image.create_on_demand)
        jpg.image.create_on_demand = True
        self.assertTrue(jpg.image.create_on_demand)
        self.assertRaises(
            ValueError,
            self.try_invalid_create_on_demand_set
        )

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

    @staticmethod
    def invalid_image_warmer():
        """
        Instantiates a VersatileImageFieldWarmer with something other than
        a model instance or queryset.
        Should raise ValueError
        """
        invalid_warmer = VersatileImageFieldWarmer(
            instance_or_queryset=['invalid'],
            rendition_key_set=(
                ('test_thumb', 'thumbnail__100x100'),
            ),
            image_attr='image'
        )
        del invalid_warmer

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
                ('test_crop', 'crop__100x100'),
                ('test_invert', 'filters__invert__url'),
            ),
            image_attr='image',
            verbose=True
        )
        num_created, failed_to_create = all_imgs_warmer.warm()
        self.assertRaises(
            ValueError,
            self.invalid_image_warmer
        )

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
                'test_invert': (
                    '/media/__filtered__/python-logo__invert__.jpg'
                ),
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
        self.assertInHTML(
            (
                '<img src="/media/__sized__/python-logo-thumbnail-300x300.png"'
                ' id="image_0_imagepreview" data-hidden_field_id="id_image_1"'
                ' data-point_stage_id="image_0_point-stage" '
                'data-ppoi_id="image_0_ppoi" class="sizedimage-preview"/>'
            ),
            str(response.content)
        )
        self.assertInHTML(
            (
                '<script type="text/javascript" src="/static/'
                'versatileimagefield/js/versatileimagefield.js"></script>'
            ),
            str(response.content)
        )
        self.assertTrue(
            self.png.image.field.storage.exists(
                self.png.image.thumbnail['300x300'].name
            )
        )

    def VersatileImageFileDescriptor__get__None(self):
        """
        Calls VersatileImageFileDescriptor.__get__ without an instance
        should raise AttributeError
        """
        x = VersatileImageFileDescriptor(self.jpg.image.name)
        VersatileImageFileDescriptor.__get__(x)

    def test_VersatileImageFileDescriptor(self):
        """
        Ensures VersatileImageFileDescriptor works as intended
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
        fieldfile_obj = self.jpg.image
        del fieldfile_obj.field
        self.jpg.image = fieldfile_obj
        img_path = self.jpg.image.path
        img_file = open(img_path, 'rb')
        self.jpg.image = img_file
        django_file = File(img_file)
        self.jpg.image = django_file
        self.assertRaises(
            AttributeError,
            self.VersatileImageFileDescriptor__get__None
        )

    def test_VersatileImageField_picklability(self):
        """
        Ensures VersatileImageField instances can be pickled/unpickled.
        """
        pickle.dump(
            self.jpg,
            open("pickletest.p", "wb")
        )
        jpg_unpickled = pickle.load(
            open("pickletest.p", "rb")
        )
        jpg_instance = jpg_unpickled
        self.assertEqual(
            jpg_instance.image.thumbnail['100x100'].url,
            '/media/__sized__/python-logo-thumbnail-100x100.jpg'
        )
        pickled_state = self.jpg.image.__getstate__()
        self.assertEqual(
            pickled_state,
            {
                '_create_on_demand': False,
                '_committed': True,
                '_file': None,
                'name': 'python-logo.jpg',
                'closed': False
            }
        )

    @staticmethod
    def non_existent_rendition_key_set():
        """
        Tries to retrieve a non-existent rendition key set.
        Should raise ImproperlyConfigured
        """
        get_rendition_key_set('does_not_exist')

    @staticmethod
    def invalid_size_key():
        """
        Tries to validate a Size Key set with an invalid size key.
        Should raise InvalidSizeKey
        """
        get_rendition_key_set('invalid_size_key')

    @staticmethod
    def invalid_size_key_set():
        """
        Tries to retrieve a non-existent rendition key set.
        Should raise InvalidSizeKeySet
        """
        get_rendition_key_set('invalid_set')

    def test_VERSATILEIMAGEFIELD_RENDITION_KEY_SETS_setting(self):
        """
        Ensures VERSATILEIMAGEFIELD_RENDITION_KEY_SETS setting
        validates correctly
        """
        self.assertRaises(
            ImproperlyConfigured,
            self.non_existent_rendition_key_set
        )
        self.assertRaises(
            InvalidSizeKeySet,
            self.invalid_size_key_set
        )
        self.assertRaises(
            InvalidSizeKey,
            self.invalid_size_key
        )

    def __test_exif_orientation_rotate_180(self):
        """
        Ensures VersatileImageFields process exif orientation==3 data properly
        """
        exif_3 = VersatileImageTestModel.objects.get(
            img_type='exif_3'
        )
        exif_3.image.create_on_demand = True
        exif_3_path = exif_3.image.thumbnail['100x100'].name
        exif_3_img = exif_3.image.field.storage.open(
            exif_3_path
        )
        exif_3_control = exif_3.image.field.storage.open(
            'verify-against/exif-orientation-examples/'
            'Landscape_3-thumbnail-100x100.jpg'
        )
        img = Image.open(exif_3_img)
        control_img = Image.open(exif_3_control)
        self.assertTrue(
            self.imageEqual(
                img,
                control_img
            )
        )

    def __test_exif_orientation_rotate_270(self):
        """
        Ensures VersatileImageFields process exif orientation==6 data properly
        """
        exif_6 = VersatileImageTestModel.objects.get(
            img_type='exif_6'
        )
        exif_6.image.create_on_demand = True
        exif_6_img = exif_6.image.field.storage.open(
            exif_6.image.thumbnail['100x100'].name
        )
        exif_6_control = exif_6.image.field.storage.open(
            'verify-against/exif-orientation-examples/'
            'Landscape_6-thumbnail-100x100.jpg'
        )
        self.assertTrue(
            self.imageEqual(
                Image.open(exif_6_img),
                Image.open(exif_6_control)
            )
        )

    def __test_exif_orientation_rotate_90(self):
        """
        Ensures VersatileImageFields process exif orientation==8 data properly
        """
        exif_8 = VersatileImageTestModel.objects.get(
            img_type='exif_8'
        )
        exif_8.image.create_on_demand = True
        exif_8_img = exif_8.image.field.storage.open(
            exif_8.image.thumbnail['100x100'].name
        )
        exif_8_control = exif_8.image.field.storage.open(
            'verify-against/exif-orientation-examples/'
            'Landscape_8-thumbnail-100x100.jpg'
        )
        self.assertTrue(
            self.imageEqual(
                Image.open(exif_8_img),
                Image.open(exif_8_control)
            )
        )

    def test_horizontal_and_vertical_crop(self):
        """
        Tests horizontal and vertical crops with 'extreme' PPOI values
        """
        test_gif = VersatileImageTestModel.objects.get(
            img_type='gif'
        )
        test_gif.image.create_on_demand = True
        test_gif.image.ppoi = (0, 0)
        # Vertical w/ PPOI == '0x0'
        vertical_image_crop = test_gif.image.field.storage.open(
            test_gif.image.crop['30x100'].name
        )
        vertical_image_crop_control = test_gif.image.field.storage.open(
            'verify-against/python-logo-crop-c0__0-30x100.gif'
        )
        self.assertTrue(
            self.imageEqual(
                Image.open(vertical_image_crop),
                Image.open(vertical_image_crop_control)
            )
        )
        # Horizontal w/ PPOI == '0x0'
        horiz_image_crop = test_gif.image.field.storage.open(
            test_gif.image.crop['100x30'].name
        )
        horiz_image_crop_control = test_gif.image.field.storage.open(
            'verify-against/python-logo-crop-c0__0-100x30.gif'
        )
        self.assertTrue(
            self.imageEqual(
                Image.open(horiz_image_crop),
                Image.open(horiz_image_crop_control)
            )
        )

        test_gif.image.ppoi = (1, 1)
        # Vertical w/ PPOI == '1x1'
        vertical_image_crop = test_gif.image.field.storage.open(
            test_gif.image.crop['30x100'].name
        )
        vertical_image_crop_control = test_gif.image.field.storage.open(
            'verify-against/python-logo-crop-c1__1-30x100.gif'
        )
        self.assertTrue(
            self.imageEqual(
                Image.open(vertical_image_crop),
                Image.open(vertical_image_crop_control)
            )
        )
        # Horizontal w/ PPOI == '1x1'
        horiz_image_crop = test_gif.image.field.storage.open(
            test_gif.image.crop['100x30'].name
        )
        horiz_image_crop_control = test_gif.image.field.storage.open(
            'verify-against/python-logo-crop-c1__1-100x30.gif'
        )
        self.assertTrue(
            self.imageEqual(
                Image.open(horiz_image_crop),
                Image.open(horiz_image_crop_control)
            )
        )

    def test_DummyFilter(self):
        """Tests placeholder image functionality for filters"""
        test_jpg = VersatileImageTestModel.objects.get(
            img_type='png'
        )
        test_jpg.optional_image.create_on_demand = True
        test_jpg.optional_image.filters.invert.url

    @staticmethod
    def assign_crop_key():
        """
        Attempts to assign a value to the 'crop' SizedImage subclass

        Should raise NotImplementedError
        """
        jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        jpg.image.crop['100x100'] = None

    @staticmethod
    def assign_thumbnail_key():
        """
        Attempts to assign a value to the 'thumbnail' SizedImage subclass

        Should raise NotImplementedError
        """
        jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        jpg.image.thumbnail['100x100'] = None

    def test_crop_and_thumbnail_key_assignment(self):
        """Tests placeholder image functionality for filters"""
        self.assertRaises(
            NotImplementedError,
            self.assign_crop_key
        )
        self.assertRaises(
            NotImplementedError,
            self.assign_thumbnail_key
        )

    def get_bad_sized_image_key(self):
        """Attempts to retrieve a thumbnail image with a malformed size key"""
        self.jpg.image.thumbnail['fooxbar']

    def test_MalformedSizedImageKey(self):
        """
        Testing MalformedSizedImageKey exception
        """
        self.assertRaises(
            MalformedSizedImageKey,
            self.get_bad_sized_image_key
        )

    @staticmethod
    def register_invalid_sizer():
        class A(object):
            pass
        versatileimagefield_registry.register_sizer('a', A)

    @staticmethod
    def register_invalid_filter():
        class A(object):
            pass
        versatileimagefield_registry.register_filter('a', A)

    @staticmethod
    def register_invalid_sizer_name():
        versatileimagefield_registry.register_sizer('chunks', CroppedImage)

    @staticmethod
    def register_invalid_filter_name():
        versatileimagefield_registry.register_filter('_poop', InvertImage)

    @staticmethod
    def register_with_already_registered_sizer_name():
        versatileimagefield_registry.register_sizer('crop', CroppedImage)

    @staticmethod
    def register_with_already_registered_filter_name():
        versatileimagefield_registry.register_filter('invert', InvertImage)

    @staticmethod
    def unregister_non_existant_sizer():
        versatileimagefield_registry.unregister_sizer('poop')

    @staticmethod
    def unregister_non_existant_filter():
        versatileimagefield_registry.unregister_filter('poop')

    def test_registration_exceptions(self):
        """
        Ensures all registration-related exceptions fire as expected
        """
        self.assertRaises(
            InvalidSizedImageSubclass,
            self.register_invalid_sizer
        )
        self.assertRaises(
            InvalidFilteredImageSubclass,
            self.register_invalid_filter
        )
        self.assertRaises(
            UnallowedSizerName,
            self.register_invalid_sizer_name
        )
        self.assertRaises(
            UnallowedFilterName,
            self.register_invalid_filter_name
        )
        self.assertRaises(
            AlreadyRegistered,
            self.register_with_already_registered_sizer_name
        )
        self.assertRaises(
            AlreadyRegistered,
            self.register_with_already_registered_filter_name
        )
        self.assertRaises(
            NotRegistered,
            self.unregister_non_existant_sizer
        )
        self.assertRaises(
            NotRegistered,
            self.unregister_non_existant_filter
        )

    def test_unregister_methods(self):
        """
        Ensuring versatileimagefield_registry unregister methods
        work as expected
        """
        self.assertTrue(
            'crop' in versatileimagefield_registry._sizedimage_registry
        )
        versatileimagefield_registry.unregister_sizer('crop')
        self.assertFalse(
            'crop' in versatileimagefield_registry._sizedimage_registry
        )

        self.assertTrue(
            'invert' in versatileimagefield_registry._filter_registry
        )
        versatileimagefield_registry.unregister_filter('invert')
        self.assertFalse(
            'invert' in versatileimagefield_registry._filter_registry
        )

    def test_save_form_data(self):
        """
        Testing VersatileImageField.save_form_data
        """
        with open(
            os.path.join(
                os.path.dirname(upath(__file__)),
                "test.png"
            ),
            'rb'
        ) as fp:
            image_data = fp.read()
        with open(
            os.path.join(
                os.path.dirname(upath(__file__)),
                "test2.png"
            ),
            'rb'
        ) as fp:
            image_data2 = fp.read()
        # Testing new uploads
        f = VersatileImageTestModelForm(
            data={'img_type': 'xxx'},
            files={
                'image_0': SimpleUploadedFile('test.png', image_data),
                'optional_image_0': SimpleUploadedFile(
                    'test2.png', image_data2
                )
            }
        )
        self.assertEqual(f.is_valid(), True)
        self.assertEqual(type(f.cleaned_data['image'][0]), SimpleUploadedFile)
        self.assertEqual(
            type(f.cleaned_data['optional_image'][0]), SimpleUploadedFile
        )
        instance = f.save()
        self.assertEqual(instance.image.name, './test.png')
        self.assertEqual(instance.optional_image.name, './test2.png')
        # Testing updating files / PPOI values
        # Deleting optional_image file (since it'll be cleared with the
        # next form)
        instance.optional_image.delete()
        f2 = VersatileImageTestModelForm(
            data={
                'img_type': 'xxx',
                'image_0': '',
                'image_1': '0.25x0.25',
                'optional_image_0-clear': 'on'
            },
            instance=instance
        )
        instance = f2.save()
        self.assertEqual(instance.image.ppoi, (0.25, 0.25))
        self.assertEqual(instance.optional_image.name, '')
        instance.image.delete()

    @staticmethod
    def SizedImage_with_no_filename_key():
        class SizedImageSubclass(SizedImage):
            pass

        SizedImageSubclass('', '', False)

    @staticmethod
    def SizedImage_no_process_image():
        class SizedImageSubclass(SizedImage):
            filename_key = 'test'

        x = SizedImageSubclass('', '', False)
        x.process_image(image=None, image_format='JPEG', save_kwargs={},
                        width=100, height=100)

    def FilteredImage_no_process_image(self):
        class FilteredImageSubclass(FilteredImage):
            filename_key = 'test'

        x = FilteredImageSubclass(
            self.jpg.image.name,
            self.jpg.image.field.storage,
            False,
            filename_key='foo'
        )
        x.process_image(image=None, image_format='JPEG', save_kwargs={})

    def test_ProcessedImage_subclass_exceptions(self):
        """
        Ensures improperly constructed ProcessedImage subclasses throw
        NotImplementedError when appropriate.
        """
        self.assertRaises(
            NotImplementedError,
            self.SizedImage_with_no_filename_key
        )
        self.assertRaises(
            NotImplementedError,
            self.SizedImage_no_process_image
        )
        self.assertRaises(
            NotImplementedError,
            self.FilteredImage_no_process_image
        )

    @override_settings(
        INSTALLED_APPS=('tests.test_autodiscover',)
    )
    def test_autodiscover(self):
        """
        Ensures versatileimagefield.registry.autodiscover raises the
        appropriate exception when trying to import on versatileimage.py
        modules.
        """
        self.assertRaises(
            ImportError,
            autodiscover
        )

    @override_settings(
        VERSATILEIMAGEFIELD_USE_PLACEHOLDIT=True
    )
    def test_placeholdit(self):
        jpg = VersatileImageTestModel.objects.get(img_type='jpg')
        self.assertEqual(
            jpg.optional_image_3.filters.invert.crop['400x400'].url,
            'http://placehold.it/400x400'
        )

    def test_template_rendering(self):
        t = get_template("test-template.html")
        c = Context({
            'instance': self.jpg
        })
        rendered = t.render(c)
        self.assertHTMLEqual(
            rendered,
            """
<html>
<body>
<img id="image-crop" src="/media/__sized__/python-logo-crop-c0-25__0-25-400x400.jpg" />
<img id="image-thumbnail" src="/media/__sized__/python-logo-thumbnail-400x400.jpg" />
<img id="image-invert" src="/media/__filtered__/python-logo__invert__.jpg" />
<img id="image-invert-crop" src="/media/__sized__/__filtered__/python-logo__invert__-crop-c0-25__0-25-400x400.jpg" />
<img src="/media/__sized__/__placeholder__/placeholder-crop-c0-5__0-5-400x400.gif" id="optional-image-crop"/>
</body>
</html>
            """
        )

    def test_field_serialization(self):
        """
        Ensures VersatileImageField and PPOIField serialize correctly
        """
        output = serializers.serialize(
            'json',
            VersatileImageTestModel.objects.filter(pk=1)
        )
        self.assertJSONEqual(
            output,
            [
                {
                    "fields": {
                        "img_type": "png",
                        "ppoi": "0.5x0.5",
                        "image": "python-logo.png",
                        "optional_image_3": "",
                        "optional_image_2": "",
                        "optional_image": "python-logo.jpg"
                    },
                    "model": "tests.versatileimagetestmodel",
                    "pk": 1
                }
            ]
        )
