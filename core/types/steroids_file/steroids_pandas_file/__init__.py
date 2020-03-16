import os
from importlib import import_module

from .steroids_pandas_base_class import SteroidsPandasBaseClass

PACKAGE_NAME = "core.types.steroids_file.steroids_pandas_file"


def create_file(file, delimiter=',', quotechar="'", index_col=0, decimal=".", *args, **kwargs) \
        -> SteroidsPandasBaseClass:
    """
    Args:
        file: archivo a levantar
        *args:
        **kwargs:

    Returns:
        SteroidsFile
    """
    filename, file_extension = os.path.splitext(file.name)
    file_extension_name = file_extension[1:]
    try:
        if '.' in file_extension_name:
            module_name, class_name = file_extension_name.rsplit('.', 1)
        else:
            module_name = f"steroids_pandas_{file_extension_name.lower()}_file"
            class_name = f"SteroidsPandas{file_extension_name.capitalize()}File"
        file_module = import_module('.' + module_name, package=PACKAGE_NAME)
        file_class = getattr(file_module, class_name)
        instance = file_class(source_file=file, delimiter=delimiter, quotechar=quotechar,
                              index_col=index_col, decimal=decimal, *args, **kwargs)
    except (AttributeError, ModuleNotFoundError):
        raise ImportError(f"{file_extension_name} No es un tipo de archivo reconocido")
    else:
        if not issubclass(file_class, SteroidsPandasBaseClass):
            raise ImportError(f"Aún no existe el tipo de archivo: {file_class}")
    return instance
