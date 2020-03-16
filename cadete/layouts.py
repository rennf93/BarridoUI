from crispy_forms.layout import Layout, Fieldset, Submit
from crispy_forms.bootstrap import FormActions


class BaseFieldset:
    layout = Fieldset(
        "Datos meta",
        "config_name",
        "currency",
        "company",
        "country",
        css_class="col-md-4"
    )


class LoginFieldset:
    layout = Fieldset(
        "Acceso",
        "data_username",
        "data_password",
        css_class="col-md-4"
    )


class WebFieldset:
    layout = Fieldset(
        "Extra (Web)",
        "data_fiscal_id",
        css_class="col-md-4"
    )


class WebV2Fieldset:
    layout = Fieldset(
        "Extra (Web)",
        "data_fiscal_id",
        "url",
        css_class="col-md-4"
    )


class OnDemandFieldset:
    layout = Fieldset(
        "Fechas y horas",
        Fieldset(
            "Horario",
            "data_working_time_from",
            "data_working_time_to",
            css_class="col-md-6"
        ),
        Fieldset(
            "Reintentos",
            "data_tries_to_download",
            css_class="col-md-6"
        ),
        css_class="col-md-4"
    )


class CorreccionFieldSet:
    layout = Fieldset(
        "Corrección",
        "data_offset_days",
        "data_tries_to_download",
        css_class="col-md-2"
    )


class MailFieldset:
    layout = Fieldset(
        "Extra (Mail)",
        "data_mail",
        "data_subject"
    )


class FtpFieldset:
    layout = Fieldset(
        "Extra (Ftp)",
        "data_url",
        "data_port",
        css_class="col-md-4"
    )


class SubmitButton:
    layout = FormActions(
        Submit("submit", "Alta", css_class="btn btn-success text-uppercase"),
        css_class="col-md-12"
    )


class MailBaseLayout:
    layout = Layout(
        BaseFieldset.layout,
        MailFieldset.layout
    )


class FtpBaselayout:
    layout = Layout(
        BaseFieldset.layout,
        LoginFieldset.layout,
        FtpFieldset.layout,
        OnDemandFieldset.layout
    )


class WebBaseLayout:
    layout = Layout(
        BaseFieldset.layout,
        LoginFieldset.layout,
        WebFieldset.layout,
        OnDemandFieldset.layout,
        CorreccionFieldSet.layout,
    )


class WebV2BaseLayout:
    layout = Layout(
        BaseFieldset.layout,
        LoginFieldset.layout,
        WebV2Fieldset.layout,
        OnDemandFieldset.layout,
        CorreccionFieldSet.layout
    )


class BbvaLayout:
    layout = Layout(
        WebBaseLayout.layout,
        Fieldset("Específicos para el banco", "data_user_code", css_class="col-md-4"),
        SubmitButton.layout
    )


class BicaLayout:
    layout = Layout(
        WebBaseLayout.layout,
        Fieldset("Específicos para el banco", "version", css_class="col-md-4"),
        SubmitButton.layout
    )


class ComercioLayout:
    layout = Layout(
        MailBaseLayout.layout,
        SubmitButton.layout
    )


class ItauLayout:
    layout = Layout(
        WebBaseLayout.layout,
        Fieldset("Específicos para el banco", "data_contract_name", css_class="col-md-4"),
        SubmitButton.layout
    )


class MeridianLayout:
    layout = Layout(
        MailBaseLayout.layout,
        SubmitButton.layout
    )


class PagofacilLayout:
    layout = Layout(
        MailBaseLayout.layout,
        SubmitButton.layout
    )


class PagomiscuentasLayout:
    layout = Layout(
        WebV2BaseLayout.layout,
        SubmitButton.layout
    )


class PatagoniaLayout:
    layout = Layout(
        MailBaseLayout.layout,
        SubmitButton.layout
    )


class RapipagoLayout:
    layout = Layout(
        FtpBaselayout.layout,
        SubmitButton.layout
    )


class RoelaLayout:
    layout = Layout(
        WebBaseLayout.layout,
        SubmitButton.layout
    )
