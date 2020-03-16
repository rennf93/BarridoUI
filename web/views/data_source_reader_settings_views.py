from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateView

from core.core_barrido import CoreBarridoClient

# Data Source Reader Settings
from web.lib import get_application_description


class DataSourceReaderSettingsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = []
    template_name = "strategy/data_source_reader_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        application = self.kwargs.get("application")
        data_source_reader_settings = barrido_client.data_source_reader_settings(application)
        context["application_description"] = get_application_description(self.request, application)
        self.permission_required.append(f"core.data_source_reader_settings_access_{self.kwargs.get('application')}")
        if data_source_reader_settings:
            context["data_source_reader_settings"] = data_source_reader_settings.json()
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(data_source_reader_settings.status_code, data_source_reader_settings.reason))

        return context
