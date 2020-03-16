import pandas
import csv
import sys
import glob
import sqlalchemy.exc
from sqlalchemy import String, create_engine
from sqlalchemy_utils.functions import database_exists, create_database

from .tools.sql_tools import *
from .tools.data_tools import *
from ..types.tools.directory_tools import clean_folder
from core.types.steroids_file.steroids_pandas_file.steroids_pandas_csv_file import SteroidsPandasCsvFile

logger = get_task_logger(__name__)


class SqlService:
    JASPER_FOLDER = "misc/jaspers"

    def __init__(self, database_data):
        """
        Args:
            database_data (sqlalquemy.Engine): Motor de base de datos
        """
        self.database_engine = create_engine(database_data, echo_pool=True, pool_pre_ping=True)
        self.pandas_database_enbine = create_engine(database_data, echo_pool=True)

    def drop_table_if_exists(self, table_name):
        log_and_execute_sentence(self.database_engine, f"DROP TABLE IF EXISTS {table_name}")

    def execute_sql_query(self, query):
        conn = self.database_engine.connect()
        conn.execute(text(query))
        conn.close()

    def execute_stack_queries(self, queries_list):
        """
        Args:
            queries_list (list):
        """
        conn = self.database_engine.connect()
        for query in queries_list:
            conn.execute(text(query))
        conn.close()

    def execute_sql_file(self, sql_file, log_text=None):
        """
        Args:
            sql_file (SqlFile):
            log_text:
        Returns:

        """
        log_and_execute_file(self.database_engine, sql_file, log_text)

    def import_steroids_compressed_data(self, csv_preset, steroids_compressed_file, table_name,
                                        write_data_types_dict):
        self.create_database_if_not_exists()
        temp_folder = os.path.join(self.JASPER_FOLDER, table_name)
        os.mkdir(temp_folder)

        try:
            file_list = self.descomprimir_lista(steroids_compressed_file, temp_folder)
            data_frame = None
            headers = None
            for file in sorted(file_list):
                logger.info(f"Archivo: {file}")
                with open(file, 'rb') as csv_file:
                    steroids_pandas_csv = SteroidsPandasCsvFile(
                        csv_file,
                        delimiter=csv_preset.get_delimiter(),
                        quotechar=csv_preset.get_quotechar(),
                        index_col=csv_preset.get_index_col(),
                        decimal=csv_preset.get_decimal(),
                        header=headers
                    )
                headers = steroids_pandas_csv.get_columns_names()
                data_frame = self.data_frame_append_csv_file(steroids_pandas_csv, data_frame)
            data_frame['Id'] = data_frame['Id'].map(lambda x: float(x.replace('"', '')) if isinstance(x, str) else x)
            data_frame = data_frame.drop_duplicates('Id', 'last')

            self.data_frame_to_sql(data_frame, table_name=table_name,
                                   write_data_types=self.get_write_data_types(write_data_types_dict,
                                                                              data_frame.columns),
                                   index=False)
        finally:
            clean_folder(temp_folder, "*.csv")
            os.rmdir(temp_folder)

    def descomprimir_lista(self, steroids_compressed_file, temp_folder):
        steroids_compressed_file.decompress_files(temp_folder)
        return glob.glob(f"{temp_folder}/*.csv")

    @staticmethod
    def data_frame_append_csv_file(source_file, data_frame):
        """
        Args:
            source_file (core.types.steroids_file.steroids_pandas_file.SteroidsPandasCsvClass):
            data_frame (pandas.DataFrame)

        Returns:
        """
        columns = source_file.get_columns_names()
        read_column_types = source_file.get_dtypes(col_type=str)
        if data_frame is None:
            data_frame = pandas.DataFrame(dtype=str, columns=columns)
        with open(source_file.open().name, 'rb') as csv_file:
            pandas_csv = pandas.read_csv(
                filepath_or_buffer=csv_file,
                sep=source_file.delimiter, error_bad_lines=False, header=0,
                dtype=read_column_types, quoting=csv.QUOTE_NONE,
                infer_datetime_format=True, names=columns, encoding='utf-8'
            )
        data_frame = data_frame.append(pandas_csv)
        return data_frame

    @staticmethod
    def get_write_data_types(sql_types_dict, columns) -> dict:
        base_data_types = convert_columns_into_types_dict(String(100), columns)
        base_data_types.update(sql_types_dict)
        return base_data_types

    def data_frame_to_sql(self, data_frame, table_name, write_data_types=None, index=False, if_exists='append'):
        """
        Args:
            data_frame (pandas.DataFrame): Data Frame desde donde leer
            table_name (str): Nombre de la tabla para la query
            write_data_types (dict): Tipos de datos para la escritura de la tabla
            index (bool): Usar el índice del dataframe como índice de la tabla
            if_exists (str): Qué hacer si ya existe la tabla: {'fail', 'replace', 'append'} default 'append'

        Returns:
        Raises:
            ValueError: Si hay algun problema al escribir los datos en la base
        """
        try:
            logger.info(f"Registrando en tabla {table_name}")
            data_frame.to_sql(table_name,
                              con=self.pandas_database_enbine,
                              if_exists=if_exists, dtype=write_data_types, chunksize=10000, index=index)
            logger.info(f"Registro de tabla {table_name} exitoso!")
        except sqlalchemy.exc.DBAPIError as e:
            # N del a: La excepción que tira por defecto DBAPI es ilegible,
            # esta chanchada está puesta para poder capturar el error
            logger.error(sys.exc_info())
            raise ValueError(e)

    def create_database_if_not_exists(self):
        if not database_exists(self.database_engine.url):
            create_database(self.database_engine.url)


class SqlFile:
    def __init__(self, file_stream, tag_name):
        self.stream = file_stream
        self.tag_name = tag_name
