from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateView

from core.core_barrido import CoreBarridoClient


class AgentDataView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.agent_data_access'
    template_name = "cashio/agents_data.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        agents_data = barrido_client.agents_data()
        if agents_data:
            context["agents_data"] = agents_data.json()
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                        .format(agents_data.status_code, agents_data.reason))
        return context
