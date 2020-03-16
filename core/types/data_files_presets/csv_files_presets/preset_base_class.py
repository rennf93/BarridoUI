from abc import ABCMeta, abstractmethod


class PresetBaseClass(metaclass=ABCMeta):

    @abstractmethod
    def get_delimiter(self) -> str:
        pass

    @abstractmethod
    def get_decimal(self) -> str:
        pass

    @abstractmethod
    def get_index_col(self) -> str:
        pass

    @abstractmethod
    def get_quotechar(self) -> str:
        pass
