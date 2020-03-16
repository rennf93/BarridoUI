from . import BankBaseClass
from cadete import helpers
from cadete.forms import MeridianCreateForm


class Meridian(BankBaseClass):
    def __init__(self):
        BankBaseClass.__init__(self)

    def build_json_request(self, banco):
        banco = helpers.fill_mail(banco)
        banco = helpers.fill_bank(banco)
        banco = helpers.fill_global(banco)
        return banco

    def build_bank_form(self):
        self.form_class = MeridianCreateForm
        return self.form_class
