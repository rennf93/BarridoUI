import os

from django.conf import settings
from sqlalchemy.dialects.mysql import VARCHAR

from .additional_info_default import AdditionalInfoDefault
from core.types.steroids_file.steroids_pandas_file.steroids_pandas_csv_file import SteroidsPandasCsvFile


class Salary(AdditionalInfoDefault):

    def __init__(self, cartera_activa, sql_service, source_file):
        update_cartera_query = open(os.path.join(settings.MYSQL_SQL_DIR, "update-cartera-salary.sql"))
        self.cartera_activa = cartera_activa
        self.service_query = update_cartera_query.read().strip().format(settings.CORE_BARRIDO_DB_NAME,
                                                                        self.get_cartera_activa_name(),
                                                                        self.get_table_name())
        super().__init__(cartera_activa, sql_service, source_file)

    def to_sql(self):
        self.sql_service.data_frame_to_sql(
            data_frame=SteroidsPandasCsvFile(source_file=self.source_file, delimiter=";", quotechar='"',
                                             index_col=None, decimal=",").read(),
            table_name=self.get_table_name(),
            if_exists='replace', write_data_types={'DNI':  VARCHAR(50)}
        )
        self.sql_service.execute_sql_query("ALTER TABLE {} ADD PRIMARY KEY (DNI)".format(self.get_table_name()))
