from .additional_info_default import AdditionalInfoDefault


class CrossSelling(AdditionalInfoDefault):
    service_name = 'cross_selling'

    def __init__(self, source_file, cartera_activa, sql_service):
        self.service_query = \
            f'UPDATE {sql_service.database_engine.url.database}.{self.get_cartera_activa_name()} ca ' \
                f'JOIN {sql_service.database_engine.url.database}.{self.get_table_name()} csx ' \
                f'ON csx.externalId = ca.Id_Cliente ' \
                f'SET ca.Deuda_crossselling = csx.totalDue;'
        super().__init__(source_file, cartera_activa, sql_service)
