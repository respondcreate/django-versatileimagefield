from ast import literal_eval

from django.utils import six

class InvalidCropCenterPoint(Exception):
    pass

INVALID_CENTERPOINT_ERROR_MESSAGE = "%s is in invalid centerpoint. A valid centerpoint must provide two coordinates, one for the x axis and one for the y, where both values are between 0 and 1. You may pass it as either a two-position tuple like this: (0.5,0.5) or as a string where the two values are separated by an 'x' like this: '0.5x0.5'."

def validate_centerpoint_tuple(tup):
    """
    Validates that a
    """
    valid = True
    while valid == True:
        if len(tup) == 2 and isinstance(tup, tuple):
            for x in tup:
                if x >= 0 and x <= 1:
                    pass
                else:
                    valid = False
            break
        else:
            valid = False
    return valid

def convert_string_to_centerpoint_tuple(s):
    """
    Converts (and validates) a string with formatting:
    '%(x_axis)dx%(y_axis)d' into a two position tuple.

    Both x_axis and y_axis must be floats or ints greater
    than 0 and less than 1.
    """

    valid_centerpoint = True
    if not isinstance(s, six.string_types):
        valid_centerpoint = False
    else:
        try:
            string_split = [
                float(segment.strip())
                for segment in s.split('x')
                if float(segment.strip()) >= 0 and float(segment.strip()) <= 1
            ]
        except:
            try:
                string_split = literal_eval(s)
            except ValueError:
                valid_centerpoint = False
            else:
                tup = string_split
        else:
            tup = tuple(string_split)

        valid_centerpoint = validate_centerpoint_tuple(tup)

    if not valid_centerpoint:
        raise InvalidCropCenterPoint(INVALID_CENTERPOINT_ERROR_MESSAGE % s)
    else:
        return tup

__all__ = ['validate_centerpoint_tuple', 'convert_string_to_centerpoint_tuple']
