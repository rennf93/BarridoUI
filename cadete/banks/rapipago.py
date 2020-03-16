from . import BankBaseClass
from cadete import helpers
from cadete.forms import RapipagoCreateForm


class Rapipago(BankBaseClass):
    def __init__(self):
        BankBaseClass.__init__(self)

    def build_json_request(self, banco):
        banco = helpers.fill_bank(banco)
        banco = helpers.fill_ftp(banco)
        banco = helpers.fill_global(banco)
        banco = helpers.fill_pago_voluntario(banco)
        banco = helpers.fill_francos(banco, [])
        return banco

    def build_bank_form(self):
        self.form_class = RapipagoCreateForm
        return self.form_class
