from importlib import import_module

from web.views.models.applications.application_default import ApplicationDefault
from .application_base_class import ApplicationBaseClass


# Todo, documentarrrr
def create_application(app_name, data=None, *args, **kwargs):
    try:
        if '.' in app_name:
            module_name, class_name = app_name.rsplit('.', 1)
        else:
            module_name = app_name.lower()
            class_name = snake_to_camel(app_name)
        app_module = import_module('.' + module_name, package='web.views.models.applications')
        app_class = getattr(app_module, class_name)
        instance = app_class(data, *args, **kwargs)
    except (AttributeError, ModuleNotFoundError):
        return ApplicationDefault(data)
    else:
        if not issubclass(app_class, ApplicationBaseClass):
            raise ImportError("Aún no existe la applicación: {}".format(app_class))
    return instance


def build_applications(applications_dict):
    app_names = []
    for app in applications_dict:
        app_names.append(app["code"])
    applications = create_applications(app_names)
    return applications


# Todo, agregarle la posibilidad de obtener una lista de solo los templates locos
def build_applications_nav_template(applications_dict, current_user):
    applications = []
    for app in applications_dict:
        application = create_application(app["code"], app)
        applications.append(application.build_nav_template(app, current_user))
    return applications


def create_applications(app_names):
    applications = []
    for app_name in app_names:
        applications.append(create_application(app_name))
    return applications


def snake_to_camel(text):
    return ''.join(x.capitalize() or '_' for x in text.split('_'))
