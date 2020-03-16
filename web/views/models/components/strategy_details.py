from core.modules.module_base import ModuleBaseClass


class StrategyMain(ModuleBaseClass):
    def __init__(self, title, data, blocks):
        self.blocks = blocks
        super().__init__(title, data)

    def get_template(self):
        return 'strategy/strategy_components/main.html'


class ResumenAgentesDePago(ModuleBaseClass):
    def get_template(self):
        return 'strategy/strategy_components/resumen_agentes_pago.html'


class ResumenGeneracion(ModuleBaseClass):
    def get_template(self):
        return 'strategy/strategy_components/resumen_generacion.html'


class ArchivosGenerados(ModuleBaseClass):
    def get_template(self):
        return 'strategy/strategy_components/archivos_generados.html'


class GenericOutputFiles(ModuleBaseClass):
    def get_template(self):
        return 'strategy/strategy_components/generic_output_files.html'

class ArchivoProcesado(ModuleBaseClass):
    def get_template(self):
        return 'strategy/strategy_components/archivo_procesado.html'
