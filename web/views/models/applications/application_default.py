from .application_base_class import ApplicationBaseClass
from core.modules.components import AccordionSecondLevelListItem
from web.lib import has_access_to_app_element
from web.views.models.components.strategy_details import StrategyMain, GenericOutputFiles, ResumenGeneracion, \
    ArchivoProcesado
from core.modules.components import AccordionListItem, DataBlock, DataItem


class ApplicationDefault(ApplicationBaseClass):
    icon = "fa fa-cubes"

    MENU_ACTIONS = (("data_source_reader_settings", "Mapeo de campos"),
                    ("paying_agents_strategy", "Estrategias de Nivel I"),
                    ("buckets_strategy", "Estrategias de Buckets"),
                    ("outputs_strategy", "Estrategias de Salida"),
                    ("strategy_exec", "Ejecuciones"))

    @classmethod
    def build_default_nav_sub_menu(cls, app_name, current_user):
        second_level_list = []
        for action_code, title in cls.MENU_ACTIONS:
            if has_access_to_app_element(action_code, app_name, current_user):
                second_level_list.append(
                    AccordionSecondLevelListItem(title, action_code, app_name)
                )
        return second_level_list

    def build_nav_template(self, template, current_user):
        self.template_model = template
        second_level_items = self.build_default_nav_sub_menu(template["code"], current_user)
        return AccordionListItem(second_level_items, template["description"], self.icon)

    def ejecutar_aprobacion(self):
        pass

    def ejecutar_cancelacion(self):
        pass

    def get_strategy_executions_detail_modules(self, strategy_exec_data):
        return [
            GenericOutputFiles("", strategy_exec_data),
            ArchivoProcesado("", strategy_exec_data)
        ]

    def get_strategy_executions_detail_header(self, strategy_exec_data):
        strategy_exec_data["blocks"] = self.build_header_block_items(strategy_exec_data["strategy_process"])
        return StrategyMain(f"{strategy_exec_data['application'].capitalize()}",
                            strategy_exec_data,
                            self.build_header_block_items(strategy_exec_data["strategy_process"]))

    def build_header_block_items(self, strategy_process) -> [DataBlock]:
        """ Constructor del header de los detalles de una ejecución de estrategia
        Args:
            strategy_process: Datos del proceso de estrategia

        Returns:
            Lista de DataBlock con los datos a mostrar en el header
        """
        bloque_ciclo = DataBlock("col-md-6 col-xs-12", [
            DataItem("Nro. Envío", strategy_process["deliveryNumber"]),
            DataItem("Fecha inicio de ciclo", strategy_process["startCollectionDate"]),
            DataItem("Fecha primer quincena de ciclo", strategy_process["middleCollectionDate"]),
            DataItem("Fecha fin de ciclo", strategy_process["middleCollectionDate"])
        ])
        return [bloque_ciclo]
