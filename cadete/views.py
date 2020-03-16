from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView

from cadete import helpers
from .cadete import CadeteClient
from django.contrib import messages
from core.parsers import datetime_parser
from core.modules.components import ActionButton, ProgressBar, StepperHeader, TabberTab
import cadete.banks
import cadete.helpers
import json


class OperationsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cadete_access'
    template_name = "cadete/operations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cadete_client = CadeteClient(self.request.user)
        if context.get('filter_name'):
            operations = cadete_client.filter_operations(context['filter_name'], context['filter_value'])
        else:
            operations = cadete_client.operations()
        if operations:
            context["operations"] = operations.json(object_hook=datetime_parser)['operations']
            cadete.helpers.get_all_dates(context["operations"])
        else:
            messages.add_message(self.request, messages.ERROR, "Error al obtener las operaciones: [{}] {}"
                                 .format(operations.status_code, operations.reason))

        context["table_actions"] = []
        context["table_actions"].append(ActionButton("DETALLES", "operations_detail"))
        return context


class OperationsDetailView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cadete_access'
    template_name = "cadete/operations_detail.html"

    def get_context_data(self, **kwargs):
        context = super(OperationsDetailView, self).get_context_data(**kwargs)
        cadete_client = CadeteClient(self.request.user)
        response = cadete_client.get_operation(
            self.kwargs.get("operation_id"))
        if response.status_code == 200:
            context["operation_detail"] = response.json(object_hook=datetime_parser)
        else:
            reverse_lazy("index")
        return context


class DownloadOperationRenditionFileView(View):

    def get(self, request, **kwargs):
        cadete_client = CadeteClient(self.request.user)
        response = cadete_client.download_operation_rendition_file(self.kwargs.get("operation_id"))
        if response.status_code == 200:
            # file = io.BytesIO(base64.b64decode(response.content))
            file = response.content
            http_response = HttpResponse(file, content_type='application/octet-stream')
            http_response['Content-Disposition'] = 'attachment; filename={}'.format(
                request.GET.get("file_name", "data")
            )
            return http_response
        messages.add_message(self.request, messages.ERROR, "No se ha podido descargar el archivo")
        return HttpResponseRedirect(reverse_lazy("operations"))


class DownloadOperationRenditionFileByMD5View(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'core.cadete_access'

    def get(self, request, **kwargs):
        cadete_client = CadeteClient(self.request.user)
        response = cadete_client.download_operation_rendition_file_by_md5(self.kwargs.get("operation_md5"))
        if response.status_code == 200:
            file = response.content
            http_response = HttpResponse(file, content_type='application/octet-stream')
            http_response['Content-Disposition'] = 'attachment; filename={}'.format(
                request.GET.get("file_name", "data")
            )
            return http_response
        messages.add_message(self.request, messages.ERROR, "No se ha podido descargar el archivo")
        return HttpResponseRedirect(reverse_lazy("operations"))


class DownloadOperationWarehouseFileView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'core.cadete_access'

    def get(self, request, **kwargs):
        cadete_client = CadeteClient(self.request.user)
        response = cadete_client.download_operation_warehouse_file(kwargs["operation_id"],
                                                                   kwargs["warehouse_id"])
        filename = self.request.GET.get('filename', 'file.txt')
        if response.status_code == 200:
            # file = io.BytesIO(base64.b64decode(response.content))
            file = response.content
            http_response = HttpResponse(file, content_type='application/octet-stream')
            http_response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
            return http_response
        messages.add_message(self.request, messages.ERROR, "No se ha podido descargar el archivo")
        return HttpResponseRedirect(reverse_lazy("operations_detail",
                                                 kwargs={'operation_id': self.kwargs.get("operation_id")}))


class ConfigurationsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cadete_access'
    template_name = "cadete/configurations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cadete_client = CadeteClient(self.request.user)
        configurations = cadete_client.configurations(kwargs.get("config_type"))
        context["config_type"] = kwargs.get("config_type")
        if configurations:
            context["configurations"] = configurations.json(object_hook=datetime_parser)["items"]
        else:
            messages.add_message(self.request, messages.ERROR, "Error al obtener las operaciones: [{}] {}"
                                 .format(configurations.status_code, configurations.reason))
        return context


class ConfigurationsCreateView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "core.cadete_configuration_edit"
    template_name = "cadete/configurations_create.html"

    def get_context_data(self, **kwargs):
        context = super(ConfigurationsCreateView, self).get_context_data(**kwargs)
        steps = [TabberTab("Banco", True, True, "#"),
                 TabberTab("Datos", False, False, "#"),
                 TabberTab("Finalizar", False, False, "#")]
        context["bancos"] = cadete.banks.bancos_disponibles()
        context["stepper_header"] = StepperHeader(progress_bar=ProgressBar(0, True), steps=steps)
        return context


class ConfigurationsCreateBankView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = "core.cadete_configuration_edit"
    template_name = "cadete/configurations_create/bank_alta.html"
    bank_name = ""

    def get(self, request, *args, **kwargs):
        self.bank_name = self.kwargs.get("bank_name")
        try:
            bank = cadete.banks.create_bank(self.bank_name)
        except ImportError as ie:
            messages.add_message(self.request, messages.ERROR, ie)
            return HttpResponseRedirect(
                reverse_lazy("configurations_create", kwargs={"config_type": self.kwargs.get("config_type")})
            )
        self.form_class = bank.build_bank_form()
        return super().get(request, *args)

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ConfigurationsCreateBankView, self).get_context_data(**kwargs)
        steps = [TabberTab("Banco", True, False, "/cadete/configurations/banks/create"),
                 TabberTab("Datos", True, True, "#"),
                 TabberTab("Finalizar", False, False, "#")]
        context["stepper_header"] = StepperHeader(progress_bar=ProgressBar(50, True), steps=steps)
        context["bank_name"] = self.bank_name
        return context


class ConfigurationsAltaBankView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "core.cadete_configuration_edit"
    template_name = "cadete/configurations_create/bank_created.html"
    bank_name = ""
    create_template = ""
    data = []

    def post(self, request, *args, **kwargs):
        self.bank_name = self.kwargs.get("bank_name")
        cadete_client = CadeteClient(self.request.user)
        try:
            bank = cadete.banks.create_bank(self.bank_name)
        except ImportError as ie:
            messages.add_message(self.request, messages.ERROR, ie)
            return HttpResponseRedirect(
                reverse_lazy("configurations_create", kwargs={"config_type": self.kwargs.get("config_type")})
            )
        form = bank.build_bank_form()(request.POST.copy())
        response = cadete_client.create_bank_configuration(bank.build_json_request(form.data))
        content = json.loads(response.content)
        if response.status_code > 299 or "errors" in content:
            self.create_template = "bank_created_failure.html"
            self.postit(response, content)
        else:
            self.create_template = "bank_created_success.html"
            messages.add_message(self.request, messages.SUCCESS, "Banco creado!")
        self.data = content
        return super().get(request, args)

    def postit(self, response, content):
        if "errors" in content:
            messages.add_message(self.request, messages.ERROR, "Error al actualizar!")
            self.data = {"errors": content["errors"]}
        else:
            messages.add_message(self.request, messages.ERROR, response)

    def get_context_data(self, **kwargs):
        context = super(ConfigurationsAltaBankView, self).get_context_data(**kwargs)
        steps = [TabberTab("Banco", True, False, "/cadete/configurations/banks/create"),
                 TabberTab("Datos", True, False, "/cadete/configurations/banks/create/{}".format(self.bank_name)),
                 TabberTab("Finalizar", True, True, "#")]
        context["stepper_header"] = StepperHeader(progress_bar=ProgressBar(100, True), steps=steps)
        context["create_template"] = self.create_template
        context["banco"] = self.data
        return context


class ConfigurationsDetailView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cadete_access'
    template_name = "cadete/configurations_detail.html"

    def __init__(self):
        self.config_detail = {}
        super().__init__()

    def get(self, request, *args, **kwargs):
        cadete_client = CadeteClient(self.request.user)
        config_request = cadete_client.get_configuration(
            self.kwargs.get("config_type"), self.kwargs.get("configuration_id")
        )
        self.config_detail = config_request.json(
            object_hook=datetime_parser
        )
        if config_request.status_code > 299:
            messages.add_message(self.request, messages.ERROR, self.config_detail["message"])
            return HttpResponseRedirect(
                reverse_lazy("configurations", kwargs={"config_type": self.kwargs.get("config_type")})
            )
        else:
            return super().get(request, *args)

    def get_context_data(self, **kwargs):
        if self.request.user.has_perms('core.cadete_configuration_edit'):
            config_detail_template = "edit.html"
        else:
            config_detail_template = "show.html"
        context = super(ConfigurationsDetailView, self).get_context_data(**kwargs)
        context["detail_template"] = config_detail_template
        context["action"] = './../update'
        context["id"] = self.kwargs.get("configuration_id")
        context["config_type"] = self.kwargs.get("config_type")
        context["config_detail"] = self.config_detail
        return context


class ConfigurationsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView, View):
    permanent = False
    permission_required = 'core.cadete_access'

    def post(self, request, *args, **kwargs):
        cadete_client = CadeteClient(self.request.user)
        data = self.extract_data(parameter=request.POST['parameter'], value=request.POST['value'])
        response = cadete_client.update_configuration(
            kwargs.get('configuration_id'), update_data=data, config_type=kwargs.get('config_type'))
        content = json.loads(response.content)
        return JsonResponse(content, status=response.status_code)

    def get_redirect_url(self, *args, **kwargs):
        cadete_client = CadeteClient(self.request.user)
        data = {"enabled": self.request.GET.get("enabled")}
        response = cadete_client.update_configuration(
            kwargs.get("configuration_id"), update_data=data, config_type=kwargs.get('config_type'))
        if response.status_code == 200:
            messages.add_message(self.request, messages.SUCCESS, "Configuración actualizada.")
        else:
            messages.add_message(self.request, messages.ERROR, "La Configuración no pudo ser actualizada.")
        return reverse_lazy("configurations_detail", kwargs={
            'configuration_id': kwargs.get("configuration_id"),
            'config_type': kwargs.get("config_type")
        })

    @staticmethod
    def extract_data(parameter, value):
        if "data__" in parameter:
            response = {
                'data': {
                    parameter[6:]: value
                }
            }
        else:
            response = {parameter: value}
        return response
