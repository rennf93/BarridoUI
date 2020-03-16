import base64
import datetime
import io

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView

from core.core_barrido import CoreBarridoClient
from core.modules.components import ActionButton
from web.forms import StrategiesCreateForm, StrategiesImportForm


# Buckets Strategy
from web.lib import get_application_description


class BucketsStrategiesView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = []
    template_name = "strategy/buckets_strategy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        application = self.kwargs.get("application")
        buckets_strategies = barrido_client.buckets_strategies(application)
        self.permission_required.append(f"core.buckets_strategy_access_{application}")
        if buckets_strategies:
            context["buckets_strategies"] = buckets_strategies.json()
            context["application_description"] = get_application_description(self.request, application)
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                        .format(buckets_strategies.status_code, buckets_strategies.reason))

        context["table_actions"] = []
        context["table_actions"].append(ActionButton("DETALLES", "buckets_strategy_detail"))
        context["table_actions"].append(ActionButton("-", ""))
        context["table_actions"].append(ActionButton("Importar", "buckets_strategy_import"))
        context["table_actions"].append(ActionButton("Exportar", "buckets_strategy_export"))
        context["table_actions"].append(ActionButton("-", ""))
        context["table_actions"].append(ActionButton("Eliminar", "buckets_strategy_delete"))
        return context


class BucketsStrategiesDetailView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.buckets_strategy_access'
    template_name = "strategy/buckets_strategy_detail.html"
    application = ""

    def get_context_data(self, **kwargs):
        context = super(BucketsStrategiesDetailView, self).get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        buckets_strategy = barrido_client.get_buckets_strategy(self.kwargs.get("buckets_strategy_id"))
        if buckets_strategy:
            context["buckets_strategy"] = buckets_strategy.json()
            application = buckets_strategy.json()["application"]
            context["application"] = application
            context["application_description"] = get_application_description(self.request, application)
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                        .format(buckets_strategy.status_code, buckets_strategy.reason))
        return context


class BucketsStrategiesCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'core.cashio_access'
    form_class = StrategiesCreateForm
    template_name = "strategy/buckets_strategy_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.kwargs.get("application")
        context["application"] = application
        context["application_description"] = get_application_description(self.request, application)
        self.form_class.base_fields["application"].initial = application
        return context

    def form_valid(self, form):
        barrido_client = CoreBarridoClient()
        application = form.base_fields["application"].initial
        response = barrido_client.create_buckets_strategy(application, form.cleaned_data.get("description"))
        barrido_client.import_buckets_strategy(
            response.json().get("id"),
            form.cleaned_data.get("file")
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("buckets_strategy", kwargs={"application": self.form_class.base_fields["application"].initial})


class BucketsStrategiesImportView(LoginRequiredMixin, FormView):
    form_class = StrategiesImportForm
    template_name = "strategy/buckets_strategy_import.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        buckets_strategy = barrido_client.get_buckets_strategy(self.kwargs.get("buckets_strategy_id")).json()
        application = buckets_strategy["application"]
        context["buckets_strategy"] = buckets_strategy
        context["application"] = application
        context["application_description"] = get_application_description(self.request, application)
        self.form_class.base_fields["application"].initial = application
        return context

    def form_valid(self, form):
        barrido_client = CoreBarridoClient()
        response = barrido_client.import_buckets_strategy(
            self.kwargs.get("buckets_strategy_id"),
            form.cleaned_data.get("file")
        )
        if response.status_code == 202:
            messages.add_message(self.request, messages.SUCCESS, "Archivo importado.")
        else:
            messages.add_message(self.request, messages.ERROR, "No fue posible importar el archivo")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("buckets_strategy", kwargs={"application": self.form_class.base_fields["application"].initial})

class BucketsStrategiesExportView(LoginRequiredMixin, View):
    def get(self, request, buckets_strategy_id, **kwargs):
        barrido_client = CoreBarridoClient()
        response = barrido_client.export_buckets_strategy(buckets_strategy_id)
        if response.status_code == 200:
            file = io.BytesIO(base64.b64decode(response.content))
            http_response = HttpResponse(file, content_type='application/octet-stream')
            http_response['Content-Disposition'] = 'filename={}-{}.xls'.format(
                buckets_strategy_id,
                datetime.datetime.now().strftime("%m-%d-%y-%H%M%S")
            )
            return http_response
        messages.add_message(self.request, messages.ERROR, "No se ha podido exportar la estrategia")
        return HttpResponseRedirect(reverse_lazy("buckets_strategy", kwargs={"application": "debito_directo"}))


class BucketsStrategiesDeleteView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    permanent = False
    permission_required = 'core.cashio_access'

    def get_redirect_url(self, *args, **kwargs):
        barrido_client = CoreBarridoClient()
        response = barrido_client.delete_buckets_strategy(kwargs.get("buckets_strategy_id"))
        if response.status_code == 200:
            messages.add_message(self.request, messages.SUCCESS, "Estrategia eliminada.")
        else:
            messages.add_message(self.request, messages.ERROR, "La estrategia no pudo ser eliminada")
        return reverse_lazy("buckets_strategy", kwargs={"application": "debito_directo"})
