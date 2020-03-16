from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateView

from core.core_barrido import CoreBarridoClient
from core.modules.components import ActionButton

# Paying Agents Stratergies
from web.lib import get_application_description


class PayingAgentsStrategyView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = []
    template_name = "strategy/paying_agents_strategy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        paying_agents_strategies = barrido_client.paying_agents_strategies(self.kwargs.get("application"))
        application = self.kwargs.get("application")
        self.permission_required.append(f"core.paying_agents_strategy_access_{application}")
        if paying_agents_strategies:
            context["paying_agents_strategies"] = paying_agents_strategies.json()
            context["application"] = application
            context["application_description"] = get_application_description(self.request, application)
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(paying_agents_strategies.status_code, paying_agents_strategies.reason))

        context["table_actions"] = []
        context["table_actions"].append(ActionButton("DETALLES", "paying_agents_strategy_detail"))
        context["table_actions"].append(ActionButton("-", ""))
        context["table_actions"].append(ActionButton("Importar", "paying_agents_strategy_import"))
        context["table_actions"].append(ActionButton("Exportar", "paying_agents_strategy_export"))
        return context


class PayingAgentsStratergiesDetailView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.paying_agents_strategy_access'
    template_name = "strategy/paying_agents_strategy_detail.html"

    def get_context_data(self, **kwargs):
        context = super(PayingAgentsStratergiesDetailView, self).get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        paying_agents_strategy = barrido_client.get_paying_agents_strategies(self.kwargs.get("paying_agents_strategy_id"))
        if paying_agents_strategy:
            context["paying_agents_strategy"] = paying_agents_strategy.json()
            application = paying_agents_strategy.json()["application"]
            context["application"] = application
            context["application_description"] = get_application_description(self.request, application)
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(paying_agents_strategy.status_code, paying_agents_strategy.reason))
        return context
