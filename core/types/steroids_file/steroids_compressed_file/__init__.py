import os

from importlib import import_module
from .steroids_compressed_files_base_class import SteroidsCompressedFilesBaseClass

STEROIDS_COMPRESSED_PACKAGE_NAME = "core.types.steroids_file.steroids_compressed_file"


def create_file(file, *args, **kwargs) -> SteroidsCompressedFilesBaseClass:
    filename, file_extension = os.path.splitext(file.name)
    file_extension_name = file_extension[1:]
    try:
        if '.' in file_extension_name:
            module_name, class_name = file_extension_name.rsplit('.', 1)
        else:
            module_name = f"steroids_{file_extension_name.lower()}_file"
            class_name = f"Steroids{file_extension_name.capitalize()}File"
        file_module = import_module('.' + module_name, package=STEROIDS_COMPRESSED_PACKAGE_NAME)
        file_class = getattr(file_module, class_name)
        instance = file_class(source_file=file, *args, **kwargs)
    except (AttributeError, ModuleNotFoundError):
        raise ImportError("{} No es un tipo de archivo reconocido".format(file_extension_name))
    else:
        if not issubclass(file_class, SteroidsCompressedFilesBaseClass):
            raise ImportError("Aún no existe el tipo de archivo: {}".format(file_class))
    return instance
