from django import forms

from cadetep import helpers
from cadetep.cadetep import CadetePClient
from core.models import ManualCashin


class ManualCashinCreateForm(forms.ModelForm):
    cadetep_client = CadetePClient()
    cashin_file = forms.FileField(label="Cashin file")
    tenant = forms.ChoiceField(label="Tenant", required=True,
                               widget=forms.Select(attrs={"onChange": 'onTenantChanged()'}))
    channel = forms.ChoiceField(label="Canal", required=True,
                                widget=forms.Select(attrs={"onChange": 'onChannelChanged()'}))
    agreement = forms.ChoiceField(label="Convenio", required=True,
                                  widget=forms.Select(attrs={"onChange": 'onAgreementChanged()'}))
    agreement_type = forms.Field(label="Tipo Convenio", required=True, widget=forms.HiddenInput())

    def __init__(self, instance, *args, **kwargs):
        super(ManualCashinCreateForm, self).__init__(*args, **kwargs)
        self.fields['tenant'].choices = [(None, 'Seleccione...')] + helpers.allowed_tenants()
        self.fields['channel'].choices = [(None, 'Seleccione...')]
        self.fields['agreement'].choices = [(None, 'Seleccione...')]

    class Meta:
        model = ManualCashin
        exclude = ["user", "agreement_type"]

