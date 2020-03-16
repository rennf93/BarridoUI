from django import forms

from . import helpers
from crispy_forms.helper import FormHelper
from .layouts import BbvaLayout, BicaLayout, ComercioLayout, ItauLayout, MeridianLayout, PatagoniaLayout, \
    PagofacilLayout, PagomiscuentasLayout, RapipagoLayout, RoelaLayout


class BankCreateHelper:

    @staticmethod
    def build_helper(bank_name):
        helper = FormHelper()
        helper.form_action = "/cadete/configurations/banks/alta/{}".format(bank_name)
        return helper


class BankCreateForm(forms.Form):
    config_name = forms.CharField(label="Nombre identificatorio", max_length=100)
    bank_name = forms.CharField(label="Nombre del banco", max_length=100)
    currency = forms.CharField(label="Moneda", max_length=3,
                               widget=forms.TextInput(attrs={"placeholder": "ARS"}))
    company = forms.ChoiceField(label="Compañía", choices=helpers.companies())
    country = forms.ChoiceField(label="País", choices=helpers.paises(), widget=forms.Select())


class OnDemandForm(forms.Form):
    data_working_time_from = forms.IntegerField(label="Hora Desde", max_value=24, min_value=0)
    data_working_time_to = forms.IntegerField(label="Hora Hasta", max_value=24, min_value=0)
    data_offset_days = forms.IntegerField(label="Días hacia atrás")
    data_tries_to_download = forms.IntegerField(label="Intentos de descarga", max_value=20)
    # data_days_off = forms.MultipleChoiceField(label="Días inactivo", choices=helpers.dias_de_la_semana(),
    #                                          widget=forms.CheckboxSelectMultiple(),
    #                                          required=False)
    # (╯°□°）╯︵ ┻━┻


class LoginForm(forms.Form):
    data_username = forms.CharField(label="Usuario", max_length=20)
    data_password = forms.CharField(label="Contraseña", max_length=20, widget=forms.PasswordInput())


class BankWebCreateForm(BankCreateForm, LoginForm, OnDemandForm):
    data_convenio = forms.CharField(label="Convenio", max_length=100)
    data_fiscal_id = forms.CharField(label="ID Fiscal", max_length=100)


class BankWebV2CreateForm(BankCreateForm, LoginForm, OnDemandForm):
    data_convenio = forms.CharField(label="Convenio", max_length=100)
    data_fiscal_id = forms.CharField(label="ID Fiscal", max_length=100)
    url = forms.URLField(label="URL", max_length=100)


class BankFtpCreateForm(BankCreateForm, LoginForm, OnDemandForm):
    data_url = forms.CharField(label="Url", max_length=100)
    data_port = forms.IntegerField(label="Port", max_value=65000)


class BankMailCreateForm(BankCreateForm):
    data_mail = forms.EmailField(label="Dirección de correo", max_length=100)
    data_subject = forms.CharField(label="Asunto", max_length=100)


class BbvaCreateForm(BankWebCreateForm):
    data_user_code = forms.CharField(label="Código de usuario", max_length=100)
    helper = BankCreateHelper.build_helper("bbva")
    helper.add_layout(BbvaLayout.layout)


class BicaCreateForm(BankWebCreateForm):
    helper = BankCreateHelper.build_helper("bica")
    helper.add_layout(BicaLayout.layout)
    version = forms.ChoiceField(label="Versión", choices=((1, 1), (2, 2)))


class ComercioCreateForm(BankMailCreateForm):
    helper = BankCreateHelper.build_helper("comercio")
    helper.add_layout(ComercioLayout.layout)


class ItauCreateForm(BankWebCreateForm):
    helper = BankCreateHelper.build_helper("itau")
    helper.add_layout(ItauLayout.layout)
    data_contract_name = forms.CharField(label="Contract Name", max_length=100)


class MeridianCreateForm(BankMailCreateForm):
    helper = BankCreateHelper.build_helper("meridian")
    helper.add_layout(MeridianLayout.layout)


class PagofacilCreateForm(BankMailCreateForm):
    helper = BankCreateHelper.build_helper("pagofacil")
    helper.add_layout(PagofacilLayout.layout)


class PagomiscuentasCreateForm(BankWebV2CreateForm):
    helper = BankCreateHelper.build_helper("pagomiscuentas")
    helper.add_layout(PagomiscuentasLayout.layout)


class PatagoniaCreateForm(BankMailCreateForm):
    helper = BankCreateHelper.build_helper("patagonia")
    helper.add_layout(PatagoniaLayout.layout)


class RapipagoCreateForm(BankFtpCreateForm):
    helper = BankCreateHelper.build_helper("rapipago")
    helper.add_layout(RapipagoLayout.layout)


class RoelaCreateForm(BankWebCreateForm):
    helper = BankCreateHelper.build_helper("roela")
    helper.add_layout(RoelaLayout.layout)
