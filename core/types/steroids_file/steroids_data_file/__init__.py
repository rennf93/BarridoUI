import os
from importlib import import_module

from .steroids_data_file_base_class import SteroidsDataFileBaseClass

PACKAGE_NAME = "core.types.steroids_file.steroids_data_file"


def create_file(file, delimiter=",", quotechar="'",
                index_col=0, decimal=".", *args, **kwargs) -> SteroidsDataFileBaseClass:
    """
    Args:
        delimiter (str): Char para distinguir valores
        quotechar (str): Char que se usa para los strings literals
        index_col (int): Índice
        decimal (char): Caracter para distinguir decimal
        file (File): Ubicación del archivo a levantar
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
            module_name = f"steroids_{file_extension_name.lower()}_file"
            class_name = f"Steroids{file_extension_name.capitalize()}File"
        file_module = import_module('.' + module_name, package=PACKAGE_NAME)
        file_class = getattr(file_module, class_name)
        instance = file_class(source_file=file, delimiter=delimiter, quotechar=quotechar,
                              index_col=index_col, decimal=decimal, *args, **kwargs)
    except (AttributeError, ModuleNotFoundError):
        raise ImportError("{} No es un tipo de archivo reconocido".format(file_extension_name))
    else:
        if not issubclass(file_class, SteroidsDataFileBaseClass):
            raise ImportError("Aún no existe el tipo de archivo: {}".format(file_class))
    return instance
