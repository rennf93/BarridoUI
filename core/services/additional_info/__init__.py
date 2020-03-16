from importlib import import_module
from .additional_info_base_class import AdditionalInfoBaseClass


def additional_info_instance(info_name, cartera_activa, sql_service, source_file='', *args, **kwargs) \
        -> AdditionalInfoBaseClass:
    """
    Args:
        info_name (str): Nombre de la info adicional. Ej: 'salary'
        cartera_activa (ActiveWalletReport): Cartera Activa
        sql_service (core.services.SqlService): Instancia del SQLSERVICE a usar como nexo
        source_file (str): CSV base
        *args:
        **kwargs:

    Returns:
        AdditionalInfoBaseClass
    """
    try:
        if '.' in info_name:
            module_name, class_name = info_name.rsplit('.', 1)
        else:
            module_name = info_name.lower()
            class_name = snake_to_camel(info_name)
        app_module = import_module('.' + module_name, package='core.services.additional_info')
        app_class = getattr(app_module, class_name)
        instance = app_class(cartera_activa, sql_service, source_file, *args, **kwargs)
    except (AttributeError, ModuleNotFoundError):
        raise ImportError(f"{info_name} No es un tipo de info adicional reconocida")
    else:
        if not issubclass(app_class, AdditionalInfoBaseClass):
            raise ImportError(f"Aún no está implementada: {app_class}")
    return instance


def snake_to_camel(text):
    return ''.join(x.capitalize() or '_' for x in text.split('_'))
