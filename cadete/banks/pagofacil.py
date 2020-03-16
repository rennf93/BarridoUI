from .bank import BankBaseClass
from cadete import helpers
from cadete.forms import PagofacilCreateForm


class Pagofacil(BankBaseClass):
    def __init__(self):
        BankBaseClass.__init__(self)

    def build_json_request(self, banco):
        banco = helpers.fill_mail(banco)
        banco = helpers.fill_global(banco)
        banco = helpers.fill_bank(banco)
        banco = helpers.fill_pago_voluntario(banco)
        return banco

    def build_bank_form(self):
        self.form_class = PagofacilCreateForm
        return self.form_class
