import os
try:
    from urllib.parse import urljoin
except ImportError:     # Python 2
    from urlparse import urljoin

from django.utils.encoding import filepath_to_uri

SIZEDIMAGEFIELD_DIRECTORY_NAME = '__sized'

# PIL-supported file formats as found here:
# https://infohost.nmt.edu/tcc/help/pubs/pil/formats.html
# (PIL Identifier, mime type)
BMP  = ('BMP', 'image/bmp')
DCX  = ('DCX', 'image/dcx')
EPS  = ('eps', 'image/eps')
GIF  = ('GIF', 'image/gif')
JPEG = ('JPEG', 'image/jpeg')
PCD  = ('PCD', 'image/pcd')
PCX  = ('PCX', 'image/pcx')
PDF  = ('PDF', 'application/pdf')
PNG  = ('PNG', 'image/png')
PPM  = ('PPM', 'image/x-ppm')
PSD  = ('PSD', 'image/psd')
TIFF = ('TIFF', 'image/tiff')
XBM  = ('XBM', 'image/x-xbitmap')
XPM  = ('XPM', 'image/x-xpm')

# Mapping file extensions to PIL types/mime types
FILE_EXTENSION_MAP = {
    'png':PNG,
    'jpe':JPEG,
    'jpeg':JPEG,
    'jpg':JPEG,
    'gif':GIF,
    'bmp':BMP,
    'dib':BMP,
    'dcx':DCX,
    'eps':EPS,
    'ps':EPS,
    'pcd':PCD,
    'pcx':PCX,
    'pdf':PDF,
    'pbm':PPM,
    'pgm':PPM,
    'ppm':PPM,
    'psd':PSD,
    'tif':TIFF,
    'tiff':TIFF,
    'xbm':XBM,
    'xpm':XPM
}

def get_resized_filename(filename, width, height, filename_key):
    """
    Returns the 'resized filename' (according to `width`, `height` and `filename_key`)
    in the following format:
    `filename`-`filename_key`-`width`x`height`.ext
    """
    try:
        image_name, ext = filename.rsplit('.', 1)
    except ValueError:
        image_name = filename
        ext = 'jpg'
    return "%(image_name)s-%(filename_key)s-%(width)dx%(height)d.%(ext)s" % ({
        'image_name':image_name,
        'filename_key':filename_key,
        'width':width,
        'height':height,
        'ext':ext
    })

def get_resized_path(path_to_image, width, height, filename_key, base_url=None):
    """
    Returns the 'resized' path of `path_to_image`
    """
    if not path_to_image:
        filename = SIZEDIMAGEFIELD_PLACEHOLDER_FILENAME
        containing_folder = 'GLOBAL-PLACEHOLDER'
    else:
        containing_folder, filename = os.path.split(path_to_image)

    resized_filename = get_resized_filename(filename, width, height, filename_key)

    joined_path = os.path.join(*[
        SIZEDIMAGEFIELD_DIRECTORY_NAME,
        containing_folder,
        resized_filename
    ])

    if base_url:
        path_to_return = urljoin(base_url, filepath_to_uri(joined_path))
    else:
        path_to_return = joined_path
    # Removing spaces so this path is memcached key friendly
    return path_to_return.replace(' ', '')

def get_image_format_from_file_extension(file_ext):
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
