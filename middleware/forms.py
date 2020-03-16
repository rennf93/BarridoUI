from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from middleware.core_middleware import CoreMiddlewareClient


class CompaniesCreateForm(forms.Form):
    choices = (
        (True, 'SÍ'),
        (False, 'NO')
    )

    code = forms.CharField(label="Código", max_length=50, required=True)
    cuit = forms.CharField(label="CUIT de la compañía", max_length=11, required=True)
    mambu_url = forms.CharField(label="URL de Mambu", max_length=500, required=True)
    mambu_user = forms.CharField(label="Usuario de Mambu", max_length=100, required=True)
    mambu_pass = forms.CharField(label="Contraseña de Mambu", max_length=100, required=True)
    tax_source_key = forms.CharField(label="Tax Source Key", max_length=50, required=True)
    timezone = forms.CharField(label="Time Zone", max_length=60, required=True)
    pic_available = forms.ChoiceField(choices=choices, label="PIC Activo")
    pic_key = forms.CharField(label="PIC View Encoded Key", max_length=50, required=False)
    pic_max_amount = forms.Field(widget=forms.NumberInput(attrs=
    {
    'min':1,
    'max': 300,
    'id': 'number_field',
    'oninput': 'limit_input()'
    }), label="Monto máximo de pago PIC", required=False)

class CompaniesEditForm(forms.Form):
    choices = (
        (True, 'SÍ'),
        (False, 'NO')
    )

    code = forms.CharField(widget=forms.HiddenInput(), required=True)
    cuit = forms.CharField(label="CUIT de la compañía", max_length=11, required=True)
    tax_source_key = forms.CharField(label="Tax Source Key", max_length=50, required=True)
    timezone = forms.CharField(label="Time Zone", max_length=60, required=True)
    pic_available = forms.ChoiceField(choices=choices, label="PIC Activo")
    pic_key = forms.CharField(label="PIC View Encoded Key", max_length=50, required=False)
    pic_max_amount = forms.Field(widget=forms.NumberInput(attrs=
    {
    'min':1,
    'max': 300,
    'id': 'number_field',
    'oninput': 'limit_input()'
    }), label="Monto máximo de pago PIC", required=False)

class CompanyBankEditForm(forms.Form):
    choices = (
        (True, 'SÍ'),
        (False, 'NO')
    )

    agreement = forms.Field(widget=forms.NumberInput(attrs={'min':0}), label="Número de convenio")
    cashinAvailable = forms.ChoiceField(choices=choices, label="Habilitar cashin automático")
    maxAcceptedRate = forms.Field(widget=forms.NumberInput(attrs={'step': 0.01, 'min':0}), label="Tasa máxima de aceptación de cashin", required=False)
    validationAmountActive = forms.ChoiceField(choices=choices, label="Validacion de montos maximos")
    cashoutAvailable = forms.ChoiceField(choices=choices, label="Desembolso Automatico")
    cashoutMaxAmountByDay = forms.Field(widget=forms.NumberInput(attrs={'min':0}), label="Monto máximo de desembolsos por día", required=False)
    refundAvailable = forms.ChoiceField(choices=choices, label="Devolucion automática")
    refundMaxAmountByDay = forms.Field(widget=forms.NumberInput(attrs={'min':0}), label="Monto máximo de devoluciones por día", required=False)
    company_code = forms.Field(widget=forms.HiddenInput)
    bank_code = forms.Field(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(CompanyBankEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = 'company_bank_edit_send'
        self.helper.add_input(Submit('submit', 'Guardar'))

class CompanyBankConfigForm(forms.Form):
    choices = (
        (True, 'SÍ'),
        (False, 'NO')
    )
    bank_code = forms.ChoiceField(label="Seleccionar banco")
    agreement = forms.Field(widget=forms.NumberInput(attrs={'min':0}), label="Número de convenio")
    cashinAvailable = forms.ChoiceField(choices=choices, label="Habilitar cashin automático")
    maxAcceptedRate = forms.Field(widget=forms.NumberInput(attrs={'step': 0.01, 'min':0}), label="Tasa máxima de aceptación de cashin", required=False)
    validationAmountActive = forms.ChoiceField(choices=choices, label="Validacion de montos maximos")
    cashoutAvailable = forms.ChoiceField(choices=choices, label="Desembolso Automatico")
    cashoutMaxAmountByDay = forms.Field(widget=forms.NumberInput(attrs={'min':0}), label="Monto máximo de desembolsos por día", required=False)
    refundAvailable = forms.ChoiceField(choices=choices, label="Devolucion automática")
    refundMaxAmountByDay = forms.Field(widget=forms.NumberInput(attrs={'min':0}), label="Monto máximo de devoluciones por día", required=False)
    company_code = forms.Field(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(CompanyBankConfigForm, self).__init__(*args, **kwargs)
        core_middleware_client = CoreMiddlewareClient()
        self.fields['bank_code'].choices = [(banks.get("code"), banks.get("name"))
                                           for banks in core_middleware_client.banks().json()]
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = 'company_bank_config_send'
        self.helper.add_input(Submit('submit', 'Guardar'))
