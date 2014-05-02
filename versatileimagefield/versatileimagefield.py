import StringIO

from PIL import Image, ImageOps

from .datastructures import FilteredImage, SizedImage
from .registry import versatileimagefield_registry


class CroppedImage(SizedImage):
    """
    A SizedImage subclass that creates a 'cropped' image.

    See the `process_image` method for more details.
    """
    filename_key = 'crop'

    def ppoi_as_str(self):
        return "%s__%s" % (
            str(self.ppoi[0]).replace('.', '-'),
            str(self.ppoi[1]).replace('.', '-')
        )

    def get_filename_key(self):
        return "%s-c%s" % (
            self.filename_key,
            self.ppoi_as_str()
        )

    def process_image(self, image, image_format, save_kwargs,
                      width, height):
        """
        Returns a StringIO instance of `image` cropped to `width` and `height`

        Cropping will first reduce an image down to its longest side
        and then crop inwards centered on the Primary Point of Interest
        (as specified by `self.ppoi`)
        """
        imagefile = StringIO.StringIO()
        palette = image.getpalette()
        fit_image = ImageOps.fit(
            image=image,
            size=(width, height),
            method=Image.ANTIALIAS,
            centering=self.ppoi
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


class ThumbnailImage(SizedImage):
    """
    Sizes an image down to fit within a bounding box

    See the `process_image()` method for more information
    """

    filename_key = 'thumbnail'

    def process_image(self, image, image_format, save_kwargs,
                      width, height):
        """
        Returns a StringIO instance of `image` that will fit
        within a bounding box as specified by `width`x`height`
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
    """
    Inverts the colors of an image.

    See the `process_image()` for more specifics
    """

    filename_key = 'invert'

    def process_image(self, image, image_format, save_kwargs={}):
        """
        Returns a StringIO instance of `image` with inverted colors
        """
        imagefile = StringIO.StringIO()
        inv_image = ImageOps.invert(image)
        inv_image.save(
            imagefile,
            **save_kwargs
        )
        return imagefile

versatileimagefield_registry.register_sizer('crop', CroppedImage)
versatileimagefield_registry.register_sizer('thumbnail', ThumbnailImage)
versatileimagefield_registry.register_filter('invert', InvertImage)
