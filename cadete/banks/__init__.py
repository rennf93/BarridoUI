from importlib import import_module
from .bank import BankBaseClass
from os.path import dirname, basename, isfile
import glob


def create_bank(bank_name, *args, **kwargs):
    try:
        if '.' in bank_name:
            module_name, class_name = bank_name.rsplit('.', 1)
        else:
            module_name = bank_name.lower()
            class_name = bank_name.capitalize()
        bank_module = import_module('.' + module_name, package='cadete.banks')
        bank_class = getattr(bank_module, class_name)
        instance = bank_class(*args, **kwargs)
    except (AttributeError, ModuleNotFoundError):
        raise ImportError("{} No es un banco existente".format(bank_name))
    else:
        if not issubclass(bank_class, BankBaseClass):
            raise ImportError("Aún no existe el banco: {}".format(bank_class))
    return instance


def bancos_disponibles():
    modules = glob.glob(dirname(__file__) + "/*.py")
    return [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')
            and not f.endswith('bank.py')]
