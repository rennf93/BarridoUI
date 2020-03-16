from abc import ABCMeta, abstractmethod
from web.views.models.components.strategy_details import ModuleBaseClass
from core.modules.components import DataBlock
from typing import List


class ApplicationBaseClass(metaclass=ABCMeta):

    def __init__(self, meta_data=None):
        self.template_model = []
        self.meta_data = meta_data

    @abstractmethod
    def build_nav_template(self, template, current_user):
        pass

    @abstractmethod
    def ejecutar_aprobacion(self):
        pass

    @abstractmethod
    def ejecutar_cancelacion(self):
        pass

    @abstractmethod
    def get_strategy_executions_detail_modules(self, strategy_exec_data) -> List[ModuleBaseClass]:
        """ Trae los módulos disponibles para el detalle de la ejecución de estrategia
        Args:
            strategy_exec_data: (dict) Un diccionario con los datos de la ejecución de estrategia traídos desde la API

        Returns:
            Una lista de los Módulos a imprimir en la vista
        """
        pass

    def get_strategy_executions_detail_header(self, strategy_exec_data) -> DataBlock:
        """ Trae el bloque de datos que se añade al encabezado
        Args:
            strategy_exec_data: (dict) Un diccionario con los datos de la ejecución de estrategia traídos desde la API

        Returns:
            DataBlock con los parámetros a mostrar en el encabezado
        """
        pass
