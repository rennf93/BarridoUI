import csv

from .steroids_data_file_base_class import SteroidsDataFileBaseClass


class SteroidsCsvFile(SteroidsDataFileBaseClass):

    def __init__(self, source_file, delimiter=",", quotechar="'", index_col=0, decimal="."):
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.index_col = index_col
        self.decimal = decimal
        super().__init__(source_file)

    def open(self):
        pass

    def read(self):
        pass

    def get_columns_names(self, source_file='') -> str:
        if source_file == '':
            source_file = self.source_file
        if source_file.__class__.__name__ == 'bytes':
            return self.get_columns_from_reader(csv.reader(source_file, self.delimiter, self.quotechar))
        else:
            with open(source_file, 'rb') as csv_source:
                return self.get_columns_from_reader(csv.reader(csv_source, self.delimiter, self.quotechar))

    def get_columns_from_reader(self, reader):
        columns = reader[0]
        reader.seek(0)
        return columns

    def get_string_column_names(self, datos):
        return self.get_columns_from_reader(csv.reader(datos))
