import logging

from .additional_info_base_class import AdditionalInfoBaseClass
from core.types.steroids_file.steroids_pandas_file.steroids_pandas_csv_file import SteroidsPandasCsvFile

logger = logging.getLogger(__name__)


class AdditionalInfoDefault(AdditionalInfoBaseClass):

    def __init__(self, cartera_activa, sql_service, source_file):
        """
        Args:
            source_file (str): Ubicación del archivo csv
            cartera_activa (ActiveWalletReport): Cartera Activa
            sql_service (SqlService): Servicio de sql en core.services.sql_service
        """
        self.source_file = source_file
        self.cartera_activa = cartera_activa
        self.sql_service = sql_service

    def to_sql(self):
        try:
            self.sql_service.data_frame_to_sql(
                data_frame=SteroidsPandasCsvFile(source_file=self.source_file,
                                                 delimiter=";", quotechar='"',
                                                 index_col=None, decimal=",").read(),
                table_name=self.get_table_name(),
                if_exists='replace'
            )
        except Exception as e:
            logger.exception(e)

    def to_cartera_activa(self):
        self.sql_service.database_engine.execute(self.service_query)

    def get_table_name(self):
        return f"{self.__class__.__name__.lower()}"

    def get_cartera_activa_name(self):
        return f"cartera_activa_{self.cartera_activa.id}"
