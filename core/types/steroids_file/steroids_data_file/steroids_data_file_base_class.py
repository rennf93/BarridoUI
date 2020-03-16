from abc import abstractmethod, ABCMeta

from core.types.steroids_file.steroids_files_base_class import SteroidsFilesBaseClass


class SteroidsDataFileBaseClass(SteroidsFilesBaseClass, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, source_file):
        super().__init__(source_file)

    @abstractmethod
    def get_columns_names(self):
        pass
