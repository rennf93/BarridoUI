from core.modules.components import DataBlock, DataItem
from web.views.models.components.strategy_details import ResumenAgentesDePago, ResumenGeneracion, ArchivosGenerados
from .application_default import ApplicationDefault


class DebitoDirecto(ApplicationDefault):
    icon = "fa fa-paint-brush"

    def get_strategy_executions_detail_modules(self, strategy_exec_data):
        base_modules = [
            ResumenGeneracion("Resumen generación", strategy_exec_data),
            ResumenAgentesDePago("Resumen por agentes de pago", strategy_exec_data),
            ArchivosGenerados("Archivos Generados", strategy_exec_data)
        ]
        base_modules.extend(super().get_strategy_executions_detail_modules(strategy_exec_data))
        return base_modules

    def build_header_block_items(self, strategy_process):
        current_blocks = super().build_header_block_items(strategy_process)
        current_blocks.extend([
            DataBlock("col-md-6 col-xs-12", [
                DataItem("Fecha Pago", strategy_process["payDate"]),
                DataItem("Fecha Vencimiento", strategy_process["expiredDate"]),
                DataItem("Fecha Proceso", strategy_process["processDate"])
            ])]
        )
        return current_blocks
