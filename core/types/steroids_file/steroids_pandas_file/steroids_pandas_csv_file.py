import pandas
from pandas import DataFrame
from sqlalchemy.types import String

import core.types.steroids_file.steroids_data_file as steroids_data_factory
from .steroids_pandas_base_class import SteroidsPandasBaseClass
from core.types.tools.string_tools import clean_string


class SteroidsPandasCsvFile(SteroidsPandasBaseClass):

    def __init__(self, source_file, delimiter=",", quotechar="'", index_col=0, decimal=".", header=None):
        self.steroids_data_file = steroids_data_factory.create_file(file=source_file,
                                                                    delimiter=delimiter,
                                                                    quotechar=quotechar,
                                                                    index_col=index_col, decimal=decimal)
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.index_col = index_col
        self.decimal = decimal
        self.header = header
        super().__init__(source_file)

    def get_columns_names(self) -> list:
        if self.header:
            return self.header
        with open(self.source_file.name, 'rb') as csv_file:
            df = pandas.read_csv(csv_file, error_bad_lines=False, nrows=2)
            col_string = clean_string(list(df)[0], [',', '\n', "'"])
        return col_string.split(self.delimiter)

    def get_pandas_column_names(self, source_file):
        df = pandas.read_csv(source_file, error_bad_lines=False, nrows=1)
        col_string = clean_string(df.iloc[0].values[0], [',', '\n', "'"])
        return col_string.split(self.delimiter)

    def get_dtypes(self, source_file='', col_type=String(250)) -> dict:
        dtypes = dict()
        for column in self.get_columns_names():
            dtypes.update({column: col_type})
        return dtypes

    def open(self):
        return self.source_file

    def read(self) -> DataFrame:
        if self.header:
            header_in_csv = None
        else:
            header_in_csv = 0
        return pandas.read_csv(self.source_file, delimiter=self.delimiter,
                               quotechar=self.quotechar, index_col=self.index_col, header=header_in_csv)
