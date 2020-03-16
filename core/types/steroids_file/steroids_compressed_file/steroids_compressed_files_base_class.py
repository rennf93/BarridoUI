from abc import abstractmethod, ABCMeta

from core.types.steroids_file.steroids_files_base_class import SteroidsFilesBaseClass


class SteroidsCompressedFilesBaseClass(SteroidsFilesBaseClass, metaclass=ABCMeta):

    compressed = True

    def __init__(self, source_file):
        super().__init__(source_file)

    @abstractmethod
    def decompress_file(self, destination_file):
        pass

    @abstractmethod
    def decompress_files(self, destination_folder):
        pass

    @abstractmethod
    def pick(self, target_file_name):
        pass

    @abstractmethod
    def get_file_list(self):
        pass
