from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateView, View

from core.core_barrido import CoreBarridoClient
from core.modules.components import ActionButton


# Outputs Strategies
class OutputsStrategiesView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, View):
    template_name = "strategy/outputs_strategy.html"
    permission_required = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        outputs_strategies = barrido_client.outputs_strategies(self.kwargs.get("application"))
        self.permission_required.append(f"core.outputs_strategy_access_{self.kwargs.get('application')}")
        if outputs_strategies:
            context["outputs_strategies"] = outputs_strategies.json()
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(outputs_strategies.status_code, outputs_strategies.reason))
        context["table_actions"] = []
        context["table_actions"].append(ActionButton("DETALLES", "outputs_strategy_detail"))
        return context


class OutputsStratergiesDetailView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = []
    template_name = "strategy/outputs_strategy_detail.html"

    def get_context_data(self, **kwargs):
        context = super(OutputsStratergiesDetailView, self).get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        outputs_strategy = barrido_client.get_paying_agents_strategies(self.kwargs.get("outputs_strategy_id"))
        self.permission_required.append(f"core.outputs_strategy_access_{self.kwargs.get('application')}")
        if outputs_strategy:
            context["outputs_strategy"] = outputs_strategy.json()
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(outputs_strategy.status_code, outputs_strategy.reason))
        return context
