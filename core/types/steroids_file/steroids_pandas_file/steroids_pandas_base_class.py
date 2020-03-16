from abc import ABCMeta, abstractmethod
from sqlalchemy.types import String

from ..steroids_data_file.steroids_data_file_base_class import SteroidsDataFileBaseClass


class SteroidsPandasBaseClass(SteroidsDataFileBaseClass, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, source_file):
        super().__init__(source_file)

    @abstractmethod
    def get_dtypes(self, source_file, col_type=String(250)) -> dict:
        pass
