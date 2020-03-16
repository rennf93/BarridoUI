from abc import ABCMeta, abstractmethod


class AdditionalInfoBaseClass(metaclass=ABCMeta):
    service_name = 'base'
    service_query = ''

    @abstractmethod
    def to_sql(self):
        pass

    @abstractmethod
    def to_cartera_activa(self):
        pass
