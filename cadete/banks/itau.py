from .bank import BankBaseClass
from cadete import helpers
from cadete.forms import ItauCreateForm


class Itau(BankBaseClass):
    def __init__(self):
        BankBaseClass.__init__(self)

    def build_json_request(self, banco):
        banco = helpers.fill_web(banco)
        banco = helpers.fill_global(banco)
        banco = helpers.fill_bank(banco)
        banco = helpers.fill_francos(banco, ["Sunday", "Monday"])
        return banco

    def build_bank_form(self):
        self.form_class = ItauCreateForm
        return self.form_class
