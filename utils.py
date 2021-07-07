import importlib


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def columns(usable_width, n_columns, padding=0):
    col_width = (usable_width - padding * (n_columns + 1)) // n_columns
    x_values = [(i + 1) * padding + i * col_width for i in range(n_columns)]
    return col_width, x_values


def fullname(o):
    klass = o.__class__
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__ # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ValueError(msg)

    module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        raise ValueError(msg)