import os
from importlib import import_module

from .steroids_files_base_class import SteroidsFilesBaseClass
import core.types.steroids_file.steroids_compressed_file

PACKAGE_NAME = "core.types.steroids_file"


def create_file(file, *args, **kwargs) -> SteroidsFilesBaseClass:
    """
    Args:
        file (str): Ubicación del archivo a levantar
        *args:
        **kwargs:

    Returns:
        SteroidsFile
    """
    filename, file_extension = os.path.splitext(file)
    file_extension_name = file_extension[1:]
    try:
        if '.' in file_extension_name:
            module_name, class_name = file_extension_name.rsplit('.', 1)
        else:
            module_name = f"steroids_{file_extension_name.lower()}_file"
            class_name = f"Steroids{file_extension_name.capitalize()}File"
        file_module = import_module('.' + module_name, package=PACKAGE_NAME)
        file_class = getattr(file_module, class_name)
        instance = file_class(source_file=file, *args, **kwargs)
    except (AttributeError, ModuleNotFoundError):
        return core.types.steroids_file.steroids_compressed_file.create_file(file_extension_name, *args, **kwargs)
    else:
        if not issubclass(file_class, SteroidsFilesBaseClass):
            raise ImportError("Aún no existe el tipo de archivo: {}".format(file_class))
    return instance
