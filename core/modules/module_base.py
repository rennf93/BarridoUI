from abc import ABCMeta, abstractmethod


class ModuleBaseClass(metaclass=ABCMeta):
    """ ModuleBaseClass Base para módulos dinámicos.

        Attributes:
            title (str): Título para el módulo.
            data (dict): Diccionario para usar en el context del template.
    """
    def __init__(self, title, data):
        self.title = title
        self.data = data

    @abstractmethod
    def get_template(self) -> str:
        """
        Returns:
            String con el nombre del template
        """
        pass
