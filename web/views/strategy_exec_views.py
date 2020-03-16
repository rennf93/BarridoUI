import base64
import datetime
import io
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView

from core.core_barrido import CoreBarridoClient
from core.parsers import datetime_parser
from web.forms import StrategyExecutionsNewForm
from web.lib import get_application_description, get_response_message
from web.views.models import applications


class StrategyExecutionsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = []
    template_name = "strategy/strategy_exec.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        application_name = self.kwargs.get("application")
        context["application_name"] = application_name
        context["application_description"] = get_application_description(self.request, application_name)
        strategy_exec = barrido_client.strategy_executions(application_name)
        self.permission_required.append(f"core.strategy_exec_access_{application_name}")
        if strategy_exec:
            context["strategy_executions"] = strategy_exec.json(object_hook=datetime_parser)
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(strategy_exec.status_code, strategy_exec.reason))

        return context


class StrategyExecutionsDetailView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cashio_access'
    template_name = "strategy/strategy_exec_detail.html"

    def get_context_data(self, **kwargs):
        context = super(StrategyExecutionsDetailView, self).get_context_data(**kwargs)
        barrido_client = CoreBarridoClient()
        stg_exec = barrido_client.get_strategy_executions(
            self.kwargs.get("strategy_exec_id")).json(object_hook=datetime_parser)
        application_name = stg_exec["application"]
        context["strategy_execution_detail"] = stg_exec
        application = applications.create_application(application_name)
        context["modules"] = application.get_strategy_executions_detail_modules(stg_exec)
        context["header"] = application.get_strategy_executions_detail_header(stg_exec)
        context["application_name"] = application_name
        context["application_description"] = get_application_description(self.request, application_name)
        return context


class StrategyExecutionsExportView(LoginRequiredMixin, View):
    def get(self, request, strategy_exec_id, **kwargs):
        barrido_client = CoreBarridoClient()
        response = barrido_client.export_strategy_executions(strategy_exec_id)
        if response.status_code == 200:
            file = io.BytesIO(base64.b64decode(response.content))
            http_response = HttpResponse(file, content_type='application/octet-stream')
            http_response['Content-Disposition'] = 'filename={}-{}.zip'.format(
                request.GET.get("description", "data"),
                datetime.datetime.now().strftime("%m-%d-%y-%H%M%S")
            )
            return http_response
        msg = get_response_message(response)
        messages.add_message(self.request, messages.ERROR, "No se ha podido exportar la ejecucion: " + msg)
        return HttpResponseRedirect(reverse_lazy("strategy_exec_detail", kwargs={"strategy_exec_id": strategy_exec_id}))


class DownloadFileView(LoginRequiredMixin, View):
    def get(self, request, file_storage_key, **kwargs):
        barrido_client = CoreBarridoClient()
        response = barrido_client.download_file_storage(file_storage_key)
        if response.status_code == 200:
            file = io.BytesIO(base64.b64decode(response.content))
            http_response = HttpResponse(file, content_type='application/octet-stream')
            http_response['Content-Disposition'] = 'filename={}'.format(
                request.GET.get("file_name", "data")
            )
            return http_response
        parsed = json.loads(response.content)
        messages.add_message(self.request, messages.ERROR, "No se ha podido descargar el archivo: " + parsed["message"])
        return HttpResponseRedirect(
            reverse_lazy("strategy_exec", kwargs={"application": self.kwargs.get("application")}))


class StrategyExecutionsNewView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'core.cashio_access'
    form_class = StrategyExecutionsNewForm
    template_name = "strategy/strategy_exec_new.html"

    def get_context_data(self, **kwargs):
        application = self.kwargs.get("application")
        self.form_class.declared_fields['application'].initial = application
        context = super(StrategyExecutionsNewView, self).get_context_data(**kwargs)
        context["application"] = application
        context["application_description"] = get_application_description(self.request, application)
        self.form_class.base_fields["application"].initial = application

        return context

    def form_valid(self, form):
        data = form.cleaned_data
        barrido_client = CoreBarridoClient()
        response = barrido_client.process_active_wallet(
            data.get("application"),
            data.get("data_source_reader_settings"),
            data.get("buckets_strategy"),
            data.get("paying_agents_strategy"),
            data.get("outputs_strategy"),
            data.get("active_wallet"),
            data.get("expired_date"),
            data.get("pay_date"),
            data.get("process_date"),
            data.get("start_collection_date"),
            data.get("middle_collection_date"),
            data.get("end_collection_date"),
            self.request.user.username
        )
        if response.status_code == 202:
            messages.add_message(self.request, messages.SUCCESS,
                                 "La cartera activa se estara procesando brevemente")
        else:
            messages.add_message(self.request, messages.ERROR, "No fue posible procesar la cartera activa")
        return super(StrategyExecutionsNewView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("strategy_exec",
                            kwargs={"application": self.form_class.base_fields["application"].initial})


class StrategyExecutionsApproveView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    permanent = False
    permission_required = 'core.cashio_access'

    def get_redirect_url(self, *args, **kwargs):
        barrido_client = CoreBarridoClient()
        data = {"status": "APPROVED"}
        response = barrido_client.get_strategy_executions(kwargs.get("strategy_exec_id"))
        if response.status_code == 200:
            stg_exec = response.json(object_hook=datetime_parser)
            application_name = stg_exec["application"]
            response = barrido_client.update_strategy_executions(kwargs.get("strategy_exec_id"), update_data=data)

        if response.status_code == 200:
            messages.add_message(self.request, messages.SUCCESS, "Ejecución actualizada.")
        else:
            messages.add_message(self.request, messages.ERROR, f"La Ejecución no pudo ser actualizada:"
                                                               f" {get_response_message(response)}")

        if len(application_name) > 0:
            return reverse_lazy("strategy_exec",  kwargs={"application": application_name})
        else:
            return reverse_lazy("index")


class StrategyExecutionsCancelView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    permanent = False
    permission_required = 'core.cashio_access'

    def get_redirect_url(self, *args, **kwargs):
        barrido_client = CoreBarridoClient()
        data = {"status": "CANCELED"}
        response = barrido_client.get_strategy_executions(kwargs.get("strategy_exec_id"))
        if response.status_code == 200:
            stg_exec = response.json(object_hook=datetime_parser)
            application_name = stg_exec["application"]
            response = barrido_client.update_strategy_executions(kwargs.get("strategy_exec_id"), update_data=data)

        if response.status_code == 200:
            messages.add_message(self.request, messages.SUCCESS, "Ejecución actualizada.")
        else:
            messages.add_message(self.request, messages.ERROR, f"La Ejecución no pudo ser actualizada:"
                                                               f" {get_response_message(response)}")

        if len(application_name) > 0:
            return reverse_lazy("strategy_exec",  kwargs={"application": application_name})
        else:
            return reverse_lazy("index")


class StrategyExecutionsApproveCancelAgentView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    permanent = False
    permission_required = 'core.cashio_access'

    def get_redirect_url(self, *args, **kwargs):
        barrido_client = CoreBarridoClient()
        if kwargs.get("action_id") == 'CANCEL':
            response = barrido_client.cancel_strategy_executions_agent(kwargs.get("strategy_exec_id"),
                                                                       kwargs.get("agent_code"))
        else:
            response = barrido_client.approve_strategy_executions_agent(kwargs.get("strategy_exec_id"),
                                                                        kwargs.get("agent_code"))

        if response.status_code == 200:
            messages.add_message(self.request, messages.SUCCESS, "Agente aprobado actualizada.")
        else:
            messages.add_message(self.request, messages.ERROR, "La Ejecución no pudo ser actualizada")

        return reverse_lazy("strategy_exec_detail",
                            kwargs={"strategy_exec_id": kwargs.get("strategy_exec_id")})
