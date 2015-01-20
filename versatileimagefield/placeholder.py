from __future__ import unicode_literals

import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class PlaceholderImage(object):
    """
    A class for configuring images to be used as 'placeholders' for
    blank/empty VersatileImageField fields.
    """

    def __init__(self, file, name):
        """
        `file` - A python file instance.
        `name` - The desired filename of `file`.
        """
        self.image_data = ContentFile(file.read(), name=name)
        file.close()


class OnDiscPlaceholderImage(PlaceholderImage):
    """
    A placeholder image saved to the same disc as the running
    application.
    """

    def __init__(self, path):
        """
        `path` - An absolute path to an on-disc image.
        """
        folder, name = os.path.split(path)
        file = open(path, 'rb')
        self.image_data = ContentFile(file.read(), name=name)
        super(OnDiscPlaceholderImage, self).__init__(file, name)


class OnStoragePlaceholderImage(PlaceholderImage):
    """
    A placeholder saved to a storage class. Does not necessarily need to
    be on the same storage as the field it is associated with.
    """

    def __init__(self, path, storage=None):
        """
        `path` - A path on `storage` to an Image.
        `storage` - A django storage class.
        """
        self.path = path
        storage = storage or default_storage
        file = storage.open(path)
        folder, name = os.path.split(path)
        super(OnStoragePlaceholderImage, self).__init__(file, name)
