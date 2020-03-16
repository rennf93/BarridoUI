import datetime

from django import forms

from core.core_barrido import CoreBarridoClient
from core.models import (CollectionCycle)
from core.parsers import datetime_parser


class StrategiesCreateForm(forms.Form):
    description = forms.CharField()
    file = forms.FileField()
    application = forms.CharField(widget=forms.HiddenInput(), initial="", required=False)


class StrategiesImportForm(forms.Form):
    file = forms.FileField()
    application = forms.CharField(widget=forms.HiddenInput(), initial="", required=False)


class StrategyExecutionsNewForm(forms.Form):
    # active_wallet = forms.ModelChoiceField(label="Cartera activa", queryset=ActiveWallet.objects.all())
    active_wallet = forms.FileField(label="Cartera Activa")
    data_source_reader_settings = forms.ChoiceField(label="Mapeo de campos entrada", required=True)
    paying_agents_strategy = forms.ChoiceField(label="Estrategias de Nivel I", required=False)
    buckets_strategy = forms.ChoiceField(label="Estrategia de Buckets")
    outputs_strategy = forms.ChoiceField(label="Estrategia Salidas", required=True)

    start_collection_date = forms.CharField(widget=forms.HiddenInput(), initial="")
    middle_collection_date = forms.CharField(widget=forms.HiddenInput(), initial="")
    end_collection_date = forms.CharField(widget=forms.HiddenInput(), initial="")
    validation_message = forms.CharField(widget=forms.HiddenInput(), initial="", required=False)
    application = forms.CharField(widget=forms.HiddenInput(), initial="", required=False)

    expired_date = forms.DateField(label="Fecha de vencimiento", widget=forms.TextInput(
        attrs={
            'class': 'datepicker'
        }
    ))
    pay_date = forms.DateField(label="Fecha de pago", widget=forms.TextInput(
        attrs={
            'class': 'datepicker'
        }
    ))
    process_date = forms.DateField(label="Fecha de proceso", widget=forms.TextInput(
        attrs={
            'class': 'datepicker'
        }
    ))

    def __init__(self, *args, **kwargs):
        super(StrategyExecutionsNewForm, self).__init__(*args, **kwargs)
        barrido_client = CoreBarridoClient()

        application = self.fields["application"].initial
        self.fields['data_source_reader_settings'].choices = [(dsr_setting.get("id"), dsr_setting.get("description"))
                                                              for dsr_setting in
                                                              barrido_client.data_source_reader_settings(application).json()]

        self.fields['buckets_strategy'].choices = [('', '-Seleccionar-')] + [
            (buckets_strategy.get("id"), buckets_strategy.get("description"))
            for buckets_strategy in barrido_client.buckets_strategies(application).json()]

        self.fields['paying_agents_strategy'].choices = [('', '-Seleccionar-')] + [
            (pa_strategy.get("id"), pa_strategy.get("description"))
            for pa_strategy in barrido_client.paying_agents_strategies(application).json()]

        self.fields['outputs_strategy'].choices = [(output_strategy.get("id"), output_strategy.get("description"))
                                                   for output_strategy in barrido_client.outputs_strategies(application).json()]

        collection = CollectionCycle.objects.filter(start_date__lte=datetime.date.today(),
                                                    end_date__gte=datetime.date.today()).first()

        if not collection is None:
            self.fields["start_collection_date"].initial = collection.start_date.strftime('%Y-%m-%d')
            self.fields["middle_collection_date"].initial = collection.middle_date.strftime('%Y-%m-%d')
            self.fields["end_collection_date"].initial = collection.end_date.strftime('%Y-%m-%d')
        else:
            self.fields[
                "validation_message"].initial = "No es posible crear una nueva ejecución debido a que no se encontró ningún Ciclo de Cobranza dado de alta"
