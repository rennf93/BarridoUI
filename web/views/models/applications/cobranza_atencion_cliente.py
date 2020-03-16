from web.views.models.components.strategy_details import ResumenGeneracion, ResumenAgentesDePago, ArchivosGenerados
from .application_default import ApplicationDefault


class CobranzaAtencionCliente(ApplicationDefault):

    icon = "fa fa-users"

    def get_strategy_executions_detail_modules(self, strategy_exec_data):
        base_modules = [
            ResumenGeneracion("Resumen generación", strategy_exec_data),
            ArchivosGenerados("Archivos Generados", strategy_exec_data)
        ]
        base_modules.extend(super().get_strategy_executions_detail_modules(strategy_exec_data))
        return base_modules
