import StringIO

from PIL import Image, ImageOps

from .datastructures import FilteredImage, SizedImage
from .registry import sizedimagefield_registry


class CroppedImage(SizedImage):
    filename_key = 'crop'

    def __init__(self, path_to_image, storage, crop_centerpoint=(0.5, 0.5)):
        self.crop_centerpoint = crop_centerpoint
        super(CroppedImage, self).__init__(path_to_image, storage)

    def crop_centerpoint_as_str(self):
        return "%s__%s" % (
            str(self.crop_centerpoint[0]).replace('.', '-'),
            str(self.crop_centerpoint[1]).replace('.', '-')
        )

    def get_filename_key(self):
        return "%s-c%s" % (
            self.filename_key,
            self.crop_centerpoint_as_str()
        )

    def process_image(self, image, image_format,
                      width, height, save_kwargs={}):
        """
        Crops `image` to `width` and `height`
        """
        imagefile = StringIO.StringIO()
        palette = image.getpalette()
        fit_image = ImageOps.fit(
            image=image,
            size=(width, height),
            method=Image.ANTIALIAS,
            centering=self.crop_centerpoint
        )

        # Using ImageOps.fit on GIFs can introduce issues with their palette
        # Solution derived from: http://stackoverflow.com/a/4905209/1149774
        if image_format == 'GIF':
            fit_image.putpalette(palette)

        fit_image.save(
            imagefile,
            **save_kwargs
        )

        return imagefile


class ScaledImage(SizedImage):
    filename_key = 'scale'

    def process_image(self, image, image_format,
                      width, height, save_kwargs={}):
        """
        Scales `image` to fit within `width` and `height`
        """
        imagefile = StringIO.StringIO()
        image.thumbnail(
            (width, height),
            Image.ANTIALIAS
        )
        image.save(
            imagefile,
            **save_kwargs
        )
        return imagefile


class InvertImage(FilteredImage):
    filename_key = 'invert'

    def process_filter(self, image, image_format, save_kwargs={}):
        """
        Inverts an Images Colors
        """
        imagefile = StringIO.StringIO()
        inv_image = ImageOps.invert(image)
        inv_image.save(
            imagefile,
            **save_kwargs
        )
        return imagefile

sizedimagefield_registry.register_sizer('crop', CroppedImage)
sizedimagefield_registry.register_sizer('scale', ScaledImage)
sizedimagefield_registry.register_filter('invert', InvertImage)
