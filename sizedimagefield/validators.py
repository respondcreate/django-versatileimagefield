from ast import literal_eval

from django.core.exceptions import ValidationError
from django.utils import six

INVALID_CENTERPOINT_ERROR_MESSAGE = "%s is in invalid centerpoint. A valid centerpoint must provide two coordinates, one for the x axis and one for the y, where both values are between 0 and 1. You may pass it as either a two-position tuple like this: (0.5,0.5) or as a string where the two values are separated by an 'x' like this: '0.5x0.5'."

def validate_centerpoint_tuple(value):
    """
    Validates that a tuple (`value`)...
    ...has a len of exactly 2
    ...both values are floats/ints that are greater-than-or-equal-to 0
       AND less-than-or-equal-to 1
    """
    if value:
        valid = True
    else:
        valid = False
    while valid == True:
        if len(value) == 2 and isinstance(value, tuple):
            for x in value:
                if x >= 0 and x <= 1:
                    pass
                else:
                    valid = False
            break
        else:
            valid = False
    return valid

def validate_centerpoint(value, return_converted_tuple=False):
    """
    Converts, validates and optionally returns a string with formatting:
    '%(x_axis)dx%(y_axis)d' into a two position tuple.

    If a tuple is passed to `value` it is also validated.

    Both x_axis and y_axis must be floats or ints greater
    than 0 and less than 1.
    """

    valid_centerpoint = True
    to_return = None
    if isinstance(value, tuple):
        valid_centerpoint = validate_centerpoint_tuple(value)
        if valid_centerpoint:
            to_return = value
    elif isinstance(value, six.string_types):
        tup = tuple()
        try:
            string_split = [
                float(segment.strip())
                for segment in value.split('x')
                if float(segment.strip()) >= 0 and float(segment.strip()) <= 1
            ]
        except:
            try:
                string_split = literal_eval(value)
            except ValueError:
                valid_centerpoint = False
            else:
                tup = string_split
        else:
            tup = tuple(string_split)

        valid_centerpoint = validate_centerpoint_tuple(tup)

        if valid_centerpoint:
            to_return = tup
    else:
        valid_centerpoint = False
    if not valid_centerpoint:
        raise ValidationError(
            message=INVALID_CENTERPOINT_ERROR_MESSAGE % value,
            code='invalid_centerpoint'
        )
    else:
        if to_return and return_converted_tuple is True:
            return to_return

__all__ = ['validate_centerpoint_tuple', 'validate_centerpoint']
