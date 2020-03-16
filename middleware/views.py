import io
import base64
import json

from middleware.core_middleware import CoreMiddlewareClient
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from middleware.forms import CompaniesCreateForm, CompanyBankEditForm, CompanyBankConfigForm, CompaniesEditForm
from django.contrib import messages
from core.modules.components import ActionButton
from core.modules.filters import RequestFilter
from pprint import pprint

# CashOut
# Configurar empresas
class BanksView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.bank_access'
    template_name = "cashio/banks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_filter = RequestFilter.filtro_middleware(self.request.user, '?')
        core_middleware_client = CoreMiddlewareClient()
        companies = core_middleware_client.companies(user_filter)
        if companies.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(companies.status_code, companies.reason))
        else:
            context["companies"] = companies.json()
            context["actions"] = []
            context["table_actions"] = [ActionButton("Filtrar bancos", "bank_filter", "", "")]
            context["table_actions"].append(ActionButton("Configurar banco","company_bank_config","",""))
        return context


class BankFilterView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permanent = False
    permission_required = 'core.bank_access'
    template_name = "cashio/banks_select.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        core_middleware_client = CoreMiddlewareClient()
        banks = core_middleware_client.get_banks_by_company(context["company_id"])
        if banks.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(banks.status_code, banks.reason))
        else:
            context["company"] = context["company_id"]
            context["banks"] = banks.json()
            context["table_actions"] = [ActionButton("Editar Banco", "company_bank_edit", "", "")]
        return context

class CompanyBankEdit(LoginRequiredMixin, PermissionRequiredMixin, FormView, TemplateView, HttpRequest):
    permanent = False
    permission_required = 'core.bank_access'
    template_name = "cashio/bank_company_edit.html"
    form_class = CompanyBankEditForm

    def get_initial(self):
        initial = super(CompanyBankEdit, self).get_initial()
        company_code = self.kwargs["company_code"]
        bank_code = self.kwargs["bank_code"]
        middleware_client = CoreMiddlewareClient()
        company_bank = middleware_client.get_company_bank(company_code, bank_code)
        if company_bank.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer el banco: [{}] {}"
                                 .format(company_bank.status_code, company_bank.text))
        else:
            data = company_bank.json()
            initial["name"] = data["bank"]["name"]
            initial["maxAcceptedRate"] = data["maxAcceptedRate"]
            initial["cashoutAvailable"] = data["cashoutAvailable"]
            initial["cashoutMaxAmountByDay"] = data["cashoutMaxAmountByDay"]
            initial["validationAmountActive"] = data["validationAmountActive"]
            initial["agreement"] = data["agreement"]
            initial["refundAvailable"] = data["refundAvailable"]
            initial["refundMaxAmountByDay"] = data["refundMaxAmountByDay"]
            initial["cashinAvailable"] = data["cashinAvailable"]
            initial["bank_code"] = bank_code
            initial["company_code"] = company_code
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            lele = self.request.body
            return JsonResponse(lele)
        else:
            return response


class CompanyBankPatch(LoginRequiredMixin, PermissionRequiredMixin, HttpRequest, TemplateView):
    permanent = False
    permission_required = 'core.bank_access'
    template_name = "cashio/bank_company_send.html"

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        company_bank_dictionary = request.POST.dict()
        core_mw = CoreMiddlewareClient()
        elementos_extra = {'csrfmiddlewaretoken': 'submit'}
        bank_patch = core_mw.patch_company_bank(company_bank_dictionary, company_bank_dictionary["company_code"],
                                                company_bank_dictionary["bank_code"], elementos_extra)
        message_style = messages.ERROR if int(bank_patch.status_code) > 299 else messages.INFO
        message_text = "con error!" if int(bank_patch.status_code) > 299 else "exitoso!"
        context.update(company_bank_dictionary)
        context["action"] = ActionButton("Volver a bancos", "banks", '', "")
        messages.add_message(request, message_style, "[{}] - Envío {} {}".format(
            bank_patch.status_code, message_text, bank_patch.text))
        return render(request, "cashio/bank_company_send.html", context)


# Inicio Core-Middleware
class CompaniesView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.middleware_access'
    template_name = "core_middleware/companies.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_filter = RequestFilter.filtro_middleware(self.request.user, '?')
        core_middleware_client = CoreMiddlewareClient()
        companies = core_middleware_client.companies(user_filter)
        if companies.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(companies.status_code, companies.reason))
        else:
            context["companies"] = companies.json()
            context["actions"] = []
            context["actions"].append(ActionButton("Nueva compañía",
                                                   "companies_create", 'fa-plus', ""))
            context["table_actions"] = []
            context["table_actions"].append(ActionButton("Modificar", "companies_update", "", ""))
            context["table_actions"].append(ActionButton("Eliminar", "companies_delete", "", ""))
        return context


class CompaniesCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permanent = False
    permission_required = 'core.middlware_access'
    form_class = CompaniesCreateForm
    template_name = "core_middleware/companies_create.html"

    def post(self, request, **kwargs):
        form_class = CompaniesCreateForm(request.POST)
        context = super().get_context_data(**kwargs)

        if(form_class.is_valid()):
            middleware_client = CoreMiddlewareClient()
            dic = request.POST.dict()
            response = middleware_client.create_company(
                code = dic['code'],
                cuit = dic['cuit'],
                mambu_url = dic['mambu_url'],
                mambu_user = dic['mambu_user'],
                mambu_pass = dic['mambu_pass'],
                tax_source_key = dic['tax_source_key'],
                timezone = dic['timezone'],
                pic_available = dic['pic_available'],
                pic_key = dic['pic_key'],
                pic_max_amount = dic['pic_max_amount']
            )

            context.update(dic)
            if response.status_code == 201:
                messages.add_message(self.request, messages.SUCCESS, "Compañía Creada")
                return HttpResponseRedirect(reverse_lazy("companies"))
            else:
                messages.add_message(self.request, messages.ERROR, "La compañía no pudo ser creada")
                return HttpResponseRedirect(reverse_lazy("companies_create"))

        return render(request, "core_middleware/companies_create.html", context)

class CompaniesUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FormView, TemplateView, HttpRequest):
    permanent = False
    permission_required = 'core.middlware_access'
    form_class = CompaniesEditForm
    template_name = "core_middleware/companies_update.html"

    def get_initial(self):
        initial = super(CompaniesUpdateView, self).get_initial()
        company_code = self.kwargs["company_id"]
        middleware_client = CoreMiddlewareClient()
        company = middleware_client.get_company_by_code(company_code)
        if company.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer la compañia: {}".format(company_code))
        else:
            data = company.json()
            initial["code"] = company_code
            initial["cuit"] = data[0]["cuit"]
            initial["mambu_url"] = data[0]["mambuUrl"]
            initial["mambu_user"] = data[0]["mambuUser"]
            initial["tax_source_key"] = data[0]["taxSourceKey"]
            initial["timezone"] = data[0]["timezone"]
            initial["pic_available"] = data[0]["picAvailable"]
            initial["pic_key"] = data[0]["picKey"]
            initial["pic_max_amount"] = data[0]["picMaxAmount"]
        return initial

    def post(self, request, **kwargs):
        form_class = CompaniesEditForm(request.POST)
        context = super().get_context_data(**kwargs)

        if(form_class.is_valid()):
            middleware_client = CoreMiddlewareClient()
            dic = request.POST.dict()
            response = middleware_client.update_company(
                code = dic['code'],
                cuit = dic['cuit'],
                tax_source_key = dic['tax_source_key'],
                timezone = dic['timezone'],
                pic_available = dic['pic_available'],
                pic_key = dic['pic_key'],
                pic_max_amount = dic['pic_max_amount']
            )

            context.update(dic)
            if response.status_code == 204:
                messages.add_message(self.request, messages.SUCCESS, "Compañía Modificada")
                return HttpResponseRedirect(reverse_lazy("companies"))
            else:
                messages.add_message(self.request, messages.ERROR, "La compañía no pudo ser modificada")
                return HttpResponseRedirect(reverse_lazy("companies_update", kwargs={'company_id': dic['code']}))

        return render(request, "core_middleware/companies_update.html", context)

class CompaniesDeleteView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    permanent = False
    permission_required = 'core.middleware_access'

    def get_redirect_url(self, *args, **kwargs):
        middleware_client = CoreMiddlewareClient()
        response = middleware_client.delete_company(kwargs.get("company_id"))
        if response.status_code == 200:
            messages.add_message(self.request, messages.SUCCESS, "Compañía eliminada.")
        else:
            messages.add_message(self.request, messages.ERROR, "La compañía no pudo ser eliminada")
        return reverse_lazy("companies")


class CompanyBankConfig(LoginRequiredMixin, PermissionRequiredMixin, FormView, TemplateView, HttpRequest):
    permanent = False
    permission_required = 'core.bank_access'
    template_name = "cashio/bank_company_config.html"
    form_class = CompanyBankConfigForm

    def get_initial(self):
        initial = super(CompanyBankConfig, self).get_initial()
        company_code = self.kwargs["company_id"]
        initial["company_code"] = company_code
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            body = self.request.body
            return JsonResponse(body)
        else:
            return response


class CompanyBankConfigView(LoginRequiredMixin, PermissionRequiredMixin, HttpRequest, TemplateView):
    permanent = False
    permission_required = 'core.bank_access'
    template_name = "cashio/bank_company_config_send.html"

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        company_bank_dictionary = request.POST.dict()
        core_mw = CoreMiddlewareClient()
        elementos_extra = {'csrfmiddlewaretoken': 'submit'}
        company_bank_post = core_mw.post_company_bank(company_bank_dictionary, company_bank_dictionary["company_code"],
                                                      company_bank_dictionary["bank_code"], elementos_extra)
        message_style = messages.ERROR if int(company_bank_post.status_code) > 299 else messages.INFO
        message_text = "con error!" if int(company_bank_post.status_code) > 299 else "exitoso!"
        context.update(company_bank_dictionary)
        context["action"] = ActionButton("Volver a bancos", "banks", '', "")
        messages.add_message(request, message_style, "[{}] - Envío {} {}".format(
            company_bank_post.status_code, message_text, company_bank_post.text))
        return render(request, "cashio/bank_company_config_send.html", context)

# [Cash In]
class CashinProcessStatusView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cashin_process_access'
    template_name = "core_middleware/cash_in_process_status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        core_middleware_client = CoreMiddlewareClient()
        process_status = core_middleware_client.cashin_process_status()
        if process_status.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(process_status.status_code, process_status.reason))
        else:
            context["process_status"] = process_status.json()
        return context


# [Cash Out Summaries]
class CashOutSummariesView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cashout_summaries_access'
    template_name = "core_middleware/cash_out_summaries.html"

    def get_context_data(self, **kwargs):
        user_filter = "?limit=200"
        user_filter = user_filter + RequestFilter.filtro_middleware(self.request.user, '&')
        context = super().get_context_data(**kwargs)
        core_mw = CoreMiddlewareClient()
        cash_out_summaries = core_mw.get_cash_out_summaries(user_filter)
        context["table_actions"] = []
        context["table_actions"].append(ActionButton("Ver Cash Outs", "cash_outs", "", ""))
        context["table_actions"].append(ActionButton("Descargar", "cash_outs_summary_download", "", ""))
        if cash_out_summaries.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                .format(cash_out_summaries.status_code, cash_out_summaries.reason))
        else:
            context["cash_out_summaries"] = cash_out_summaries.json()
        return context


class CashOutPrioritiesView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cashout_summaries_access'
    template_name = "core_middleware/cash_out_priorities.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.request.GET.get('company_id')
        if company_id is None:
            company_id = 2
        company_name = self.request.GET.get('company_name')
        if company_name is None:
            company_name = "Wenance"
        core_mw = CoreMiddlewareClient()
        sorted_products = core_mw.get_sorted_products(company_id)
        if sorted_products.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                 .format(sorted_products.status_code, sorted_products.reason))
        else:
            sorted_products_list = sorted_products.content.decode('utf-8').split(',')
            context["company_id"] = company_id
            context["company_name"] = company_name
            context["sorted_products"] = sorted_products_list
        return context

class CashOutPrioritiesUpdate(LoginRequiredMixin, PermissionRequiredMixin, View):
    permanent = False
    permission_required = 'core.cashout_summaries_access'

    def post(self, request, **kwargs):
        sorted_products = request.POST.get('products_string')
        core_mw = CoreMiddlewareClient()
        response = core_mw.patch_products_order(sorted_products,kwargs["company_id"])
        content = json.loads(response.content)
        return JsonResponse(content,status=response.status_code)

class CashOutsByCompanyBankSendingDateView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cashout_summaries_access'
    template_name = "core_middleware/cash_outs.html"

    def get_context_data(self, **kwargs):
        filter = "&limit=200"
        context = super().get_context_data(**kwargs)
        core_mw = CoreMiddlewareClient()
        company_id = self.request.GET.get("companyId")
        bank_id = self.request.GET.get("bankId")
        sending_date = self.request.GET.get("sendingDate")
        pprint(self.request.GET)
        # Guarda en sesión el Query String de la búsqueda Cash Outs (revisar)
        #import ipdb; ipdb.set_trace()
        self.request.session["cash_out_summaries_cash_outs_qs"] = "companyId=" + company_id + "&bankId=" + bank_id + "&sendingDate=" + sending_date
        cash_outs = core_mw.get_cash_outs_by_company_bank_sending_date(company_id, bank_id, sending_date, filter)
        if cash_outs.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                .format(cash_outs.status_code, cash_outs.reason))
        else:
            context["cash_outs"] = cash_outs.json()
            context["table_actions"] = [ActionButton("Ver Movimientos", "", "", "")]
        return context


class CashOutLoansView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cashout_summaries_access'
    template_name = "core_middleware/cash_out_loans.html"

    def get_context_data(self, **kwargs):
        filter = "?limit=200"
        context = super().get_context_data(**kwargs)
        core_mw = CoreMiddlewareClient()
        cash_out_id = self.kwargs["cash_out_id"]
        cash_out_loans = core_mw.get_cash_out_loans(cash_out_id, filter)
        if cash_out_loans.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                .format(cash_out_loans.status_code, cash_out_loans.reason))
        else:
            context["cash_out_loans"] = cash_out_loans.json()
        return context


class DownloadCashOutSummaryFileView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'core.cashout_summaries_access'

    def get(self, request, **kwargs):
        core_mw = CoreMiddlewareClient()

        company_id = self.request.GET.get("companyId")
        bank_id = self.request.GET.get("bankId")
        sending_date = self.request.GET.get("sendingDate")

        if not bank_id:
            bank_id = "3"

        response = core_mw.download_cash_out_summarie(company_id, bank_id, sending_date)
        if response.status_code == 200:
            file = io.BytesIO(base64.b64decode(response.content))
            # file = response.content
            http_response = HttpResponse(file, content_type='application/octet-stream')
            http_response['Content-Disposition'] = 'filename={}'.format("cashout_summary_{}.csv".format(sending_date))
            return http_response
        messages.add_message(self.request, messages.ERROR, "No se ha podido descargar el archivo")
        return HttpResponseRedirect(reverse_lazy("cash_outs"))

class CashInBinnacleSummaryView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cashin_binnacle_summaries_access'
    template_name = "core_middleware/cash_in_binnacle_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        core_mw = CoreMiddlewareClient()
        cash_in_summary = core_mw.get_cash_in_binnacle_summaries()
        if cash_in_summary.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                .format(cash_in_summary.status_code, cash_in_summary.reason))
        else:
            context["cash_in_binnacle_summary"] = cash_in_summary.json()
            context["table_actions"] = [ActionButton("Descargar", "cashin_binnacle_download", "", "")]
        return context


class CashInBinnacleDownloadFileView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'core.cashin_binnacle_summaries_access'

    def get(self, request, binnacle_date, **kwargs):
        barrido_client = CoreMiddlewareClient()
        response = barrido_client.get_cash_in_binnacle_summaries_download(binnacle_date)
        if response.status_code == 200:
            file = io.BytesIO(base64.b64decode(response.content))
            http_response = HttpResponse(file, content_type='application/octet-stream')
            http_response['Content-Disposition'] = 'filename=bitacora_{}.csv'.format(binnacle_date)
            return http_response
        messages.add_message(self.request, messages.ERROR, "No se ha podido descargar el archivo")
        return HttpResponseRedirect(reverse_lazy("cashin_binnacle_summary"))


class CashOutRefundsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.cashout_summaries_access'
    template_name = "core_middleware/cash_out_refunds.html"

    def get_context_data(self, **kwargs):
        filter = "?limit=200"
        context = super().get_context_data(**kwargs)
        core_mw = CoreMiddlewareClient()
        cash_out_id = self.kwargs["cash_out_id"]
        cash_out_refunds = core_mw.get_cash_out_refunds(cash_out_id, filter)
        if cash_out_refunds.status_code != 200:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                .format(cash_out_refunds.status_code, cash_out_refunds.reason))
        else:
            context["cash_out_refunds"] = cash_out_refunds.json()
        return context
