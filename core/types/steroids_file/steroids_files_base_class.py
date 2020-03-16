from abc import ABCMeta, abstractmethod


class SteroidsFilesBaseClass(metaclass=ABCMeta):

    compressed = False

    @abstractmethod
    def __init__(self, source_file):
        """
        Args:
            source_file: (File), archivo o bytes
        """
        self.source_file = source_file

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def read(self):
        pass
