from abc import ABCMeta, abstractmethod
from cadete.forms import BankCreateForm


class BankBaseClass(metaclass=ABCMeta):
    form_class = BankCreateForm

    def __init__(self):
        pass

    @abstractmethod
    def build_json_request(self, bank):
        pass

    @abstractmethod
    def build_bank_form(self):
        pass
