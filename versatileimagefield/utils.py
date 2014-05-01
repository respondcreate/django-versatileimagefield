import os

from .settings import (
    USE_PLACEHOLDIT,
    VERSATILEIMAGEFIELD_PLACEHOLDER_IMAGE,
    VERSATILEIMAGEFIELD_SIZED_DIRNAME,
    VERSATILEIMAGEFIELD_FILTERED_DIRNAME
)

if not USE_PLACEHOLDIT:
    PLACEHOLDER_FOLDER, PLACEHOLDER_FILENAME = os.path.split(
        VERSATILEIMAGEFIELD_PLACEHOLDER_IMAGE
    )

# PIL-supported file formats as found here:
# https://infohost.nmt.edu/tcc/help/pubs/pil/formats.html
# (PIL Identifier, mime type)
BMP = ('BMP', 'image/bmp')
DCX = ('DCX', 'image/dcx')
EPS = ('eps', 'image/eps')
GIF = ('GIF', 'image/gif')
JPEG = ('JPEG', 'image/jpeg')
PCD = ('PCD', 'image/pcd')
PCX = ('PCX', 'image/pcx')
PDF = ('PDF', 'application/pdf')
PNG = ('PNG', 'image/png')
PPM = ('PPM', 'image/x-ppm')
PSD = ('PSD', 'image/psd')
TIFF = ('TIFF', 'image/tiff')
XBM = ('XBM', 'image/x-xbitmap')
XPM = ('XPM', 'image/x-xpm')

# Mapping file extensions to PIL types/mime types
FILE_EXTENSION_MAP = {
    'png': PNG,
    'jpe': JPEG,
    'jpeg': JPEG,
    'jpg': JPEG,
    'gif': GIF,
    'bmp': BMP,
    'dib': BMP,
    'dcx': DCX,
    'eps': EPS,
    'ps': EPS,
    'pcd': PCD,
    'pcx': PCX,
    'pdf': PDF,
    'pbm': PPM,
    'pgm': PPM,
    'ppm': PPM,
    'psd': PSD,
    'tif': TIFF,
    'tiff': TIFF,
    'xbm': XBM,
    'xpm': XPM
}


def get_resized_filename(filename, width, height, filename_key):
    """
    Returns the 'resized filename' (according to `width`, `height` and
    `filename_key`) in the following format:
    `filename`-`filename_key`-`width`x`height`.ext
    """
    try:
        image_name, ext = filename.rsplit('.', 1)
    except ValueError:
        image_name = filename
        ext = 'jpg'
    return "%(image_name)s-%(filename_key)s-%(width)dx%(height)d.%(ext)s" % ({
        'image_name': image_name,
        'filename_key': filename_key,
        'width': width,
        'height': height,
        'ext': ext
    })


def get_resized_path(path_to_image, width, height,
                     filename_key, storage):
    """
    Returns a 2-tuple to `path_to_image` location on `storage` (position 0)
    and it's web-accessible URL (position 1) as dictated by `width`, `height`
    and `filename_key`
    """
    if not path_to_image:
        filename = PLACEHOLDER_FILENAME
        containing_folder = 'GLOBAL-PLACEHOLDER'
    else:
        containing_folder, filename = os.path.split(path_to_image)

    resized_filename = get_resized_filename(
        filename,
        width,
        height,
        filename_key
    )

    joined_path = os.path.join(*[
        VERSATILEIMAGEFIELD_SIZED_DIRNAME,
        containing_folder,
        resized_filename
    ]).replace(' ', '')  # Removing spaces so this path is memcached friendly

    return (
        joined_path,
        storage.url(joined_path)
    )


def get_filtered_filename(filename, filename_key):
    """
    Returns the 'filtered filename' (according to `filename_key`)
    in the following format:
    `filename`__`filename_key`__.ext
    """
    try:
        image_name, ext = filename.rsplit('.', 1)
    except ValueError:
        image_name = filename
        ext = 'jpg'
    return "%(image_name)s__%(filename_key)s__.%(ext)s" % ({
        'image_name': image_name,
        'filename_key': filename_key,
        'ext': ext
    })


def get_filtered_path(path_to_image, filename_key, storage):
    """
    Returns the 'filtered path' & URL of `path_to_image`
    """
    if not path_to_image:
        filename = PLACEHOLDER_FILENAME
        containing_folder = 'GLOBAL-PLACEHOLDER'
    else:
        containing_folder, filename = os.path.split(path_to_image)

    filtered_filename = get_filtered_filename(filename, filename_key)
    path_to_return = os.path.join(*[
        containing_folder,
        VERSATILEIMAGEFIELD_FILTERED_DIRNAME,
        filtered_filename
    ])
    # Removing spaces so this path is memcached key friendly
    path_to_return = path_to_return.replace(' ', '')
    return (
        path_to_return,
        storage.url(path_to_return)
    )


def get_image_metadata_from_file_ext(file_ext):
    """
    Receives a valid image file format and returns a 2-tuple of two strings:
        [0]: Image format (i.e. 'jpg', 'gif' or 'png')
        [1]: InMemoryUploadedFile-friendly save format (i.e. 'image/jpeg')
    image_format, in_memory_file_type
    """
    if file_ext not in FILE_EXTENSION_MAP:
        return JPEG
    else:
        return FILE_EXTENSION_MAP[file_ext]
