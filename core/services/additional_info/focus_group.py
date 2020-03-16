from sqlalchemy.dialects.mysql import VARCHAR

from .additional_info_default import AdditionalInfoDefault
from core.types.steroids_file.steroids_pandas_file.steroids_pandas_csv_file import SteroidsPandasCsvFile


class FocusGroup(AdditionalInfoDefault):
    service_name = 'focus_group'

    def __init__(self, source_file, cartera_activa, sql_service):
        self.service_query = \
            f'UPDATE {sql_service.database_name}.{self.get_cartera_activa_name()} ca ' \
                f'JOIN {sql_service.database_name}.{self.get_table_name()} cs ' \
                f'ON cs.dni = ca.dni ' \
                f'SET ca.Grupo = cs.grupo;'
        super().__init__(source_file, cartera_activa, sql_service)

    def to_sql(self):
        self.sql_service.data_frame_to_sql(
            data_frame=SteroidsPandasCsvFile(source_file=self.source_file, delimiter=",", quotechar='"',
                                             index_col=None, decimal=",").read(),
            table_name=self.get_table_name(),
            if_exists='replace', write_data_types={'DNI':  VARCHAR(50)}
        )
        self.sql_service.execute_sql_query("ALTER TABLE {} ADD PRIMARY KEY (DNI)".format(self.get_table_name()))
