
def _bool(value):
    """
    Returns boolean value.
    """
    value = (value or '').lower()

    if value in {'true', 't', '1'}:
        return True

    elif value in {'false', 'f', '0'}:
        return False

    raise ValueError('Cannot parse %s value to boolean' % value)


class Undefined:

    def __call__(self, value):
        """ Returns the same value """
        return value


undefined = Undefined()


def cast_param(request, param, cast=undefined, default=None):
    """
    Returns casted parameter value.
    """
    value = request.GET.get(param)

    # define default cast to boolean.
    cast = _bool if cast == bool else cast

    try:
        value = cast(value)

    except (ValueError, TypeError):
        return default

    else:
        return value
