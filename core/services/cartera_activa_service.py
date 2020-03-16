from time import sleep
from typing import List

from ..types.data_files_presets.csv_files_presets.jasper_preset import JasperPreset
from ..types.tools.string_tools import clean_string
from ..types.connections import mysql_engine
from .tools.cartera_activa_inicial_tools import *
from .tools.cartera_activa_tools import *
from .sql_service import SqlService, SqlFile
import core.types.steroids_file.steroids_compressed_file
import core.services.additional_info as additional_info
from .tools.data_tools import *
import sys


class CarteraActivaService:

    def __init__(self, cartera_activa_object):
        self.cartera_activa = cartera_activa_object
        self.database_name = settings.CORE_BARRIDO_DB_NAME
        self.barrido_ui_database_name = settings.MYSQL_NAME
        self.barrido_engine = mysql_engine(self.database_name)
        self.barrido_ui_engine = mysql_engine(self.barrido_ui_database_name)
        cartera_activa_object.save()

    def prepare(self):
        SqlService(self.barrido_engine).create_database_if_not_exists()
        SqlService(self.barrido_ui_engine).create_database_if_not_exists()

    def jasper_to_sql(self, source_file, write_data_types_dict):
        steroids_compressed_file = core.types.steroids_file.steroids_compressed_file.create_file(source_file)
        # Crear tabla cartera activa leyendo los sql de un zip con métodos de Steroids
        sql_service = SqlService(self.barrido_engine)
        sql_service.import_steroids_compressed_data(
            csv_preset=JasperPreset(),
            steroids_compressed_file=steroids_compressed_file,
            table_name=self.get_table_name(),
            write_data_types_dict=write_data_types_dict
        )
        # Crea tabla de cartera activa inicial en barrido
        create_active_wallet_initial_data_manager(sql_service, self.cartera_activa)
        # Guarda el reporte de cartera activa inicial
        save_cartera_activa_inicial_report(self.barrido_engine)
        # Ejecuta queries de actualización de cartera activa
        self.cartera_activa_update()

    def info_csv_to_ca(self, source_file, info_name):
        """
        Creará la tabla de la información correspondiente y updateará la tabla cartera activa con ella
        Args:
            source_file (str): File location
            info_name (str): Info Name: e.g.: 'Salary'
        Returns:
        """
        sql_service = SqlService(self.barrido_engine)
        add_info = additional_info.additional_info_instance(info_name=info_name, source_file=source_file,
                                                            cartera_activa=self.cartera_activa, sql_service=sql_service)
        add_info.to_sql()
        add_info.to_cartera_activa()

    def info_csv_to_sql(self, source_file, info_name):
        """
        Creará la tabla a partir de un csv
        Args:
            source_file (File):
            info_name (str): Nombre de la info adicional
        Returns:
        """
        try:
            sql_service = SqlService(self.barrido_engine)
            add_info = additional_info.additional_info_instance(info_name, self.cartera_activa,
                                                                sql_service, source_file)
            add_info.to_sql()
        except Exception as e:
            logger.error(e)

    def info_sql_to_ca(self, info_name):
        """
        Actualizará la tabla de cartera activa con la tabla de la info adicional
        Args:
            info_name (str):
        Returns:
        """
        try:
            sql_service = SqlService(self.barrido_engine)
            add_info = additional_info.additional_info_instance(info_name, self.cartera_activa, sql_service)
            add_info.to_cartera_activa()
        except Exception as e:
            logger.error(e)

    def cartera_activa_update(self):
        logger.info("executing cartera_activa_update...")
        add_columns_file = open(os.path.join(settings.MYSQL_SQL_DIR, "update-cartera-activa-columns.sql"))
        add_columns_query = add_columns_file.read().strip().format(self.get_table_name())
        update_cartera = open(os.path.join(settings.MYSQL_SQL_DIR, "update-cartera-activa.sql"))
        update_cartera_query = update_cartera.read().strip().format(settings.CORE_BARRIDO_DB_NAME, settings.MYSQL_NAME,
                                                                    self.get_table_name())
        try:
            sql_service = SqlService(self.barrido_engine)
            logger.info("executing update-cartera-activa-columns.sql...")
            sql_service.execute_sql_query(add_columns_query)
            logger.info("executing update-cartera-activa.sql...")
            sql_service.execute_sql_query(update_cartera_query)
        except Exception as e:
            print(sys.exc_info())
            raise e
        finally:
            logger.info("update-cartera-activa.sql execution done!")

    def get_table_name(self, service='cartera_activa'):
        return f"{service}_{self.cartera_activa.id}"

    def create_temporal_tables(self, sql_files: List[SqlFile]):
        sqls = SqlService(self.barrido_ui_engine)
        for sql_file in sql_files:
            sqls.execute_sql_file(sql_file.stream, sql_file.tag_name)
            logger.info(f"Table {sql_file.tag_name} cartera_activa created.")

    def get_read_csv_data_dict(self):
        convert_columns_into_types_dict(str, self.get_cartera_activa_columns())

    @staticmethod
    def get_cartera_activa_columns():
        return clean_string(TEST_COLUMNS_DOS, [',', '\n', "'"]).split('|')
