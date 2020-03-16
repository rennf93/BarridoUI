import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView

from core.core_barrido import CoreBarridoClient
from core.models import ActiveWalletProcess


# ActiveWallet
from core.parsers import datetime_parser
from web.lib import get_application_description


class ActiveWalletProcessListView(LoginRequiredMixin, ListView):
    template_name = "active_wallet_process/list.html"
    model = ActiveWalletProcess
    queryset = ActiveWalletProcess.objects.all().order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.kwargs.get("application")
        context["application_description"] = get_application_description(self.request, application)

        return context


class ActiveWalletProcessCreateView(LoginRequiredMixin, RedirectView):
    permanent = False

    def verify_preconditions(self):
        ret = []
        status = CoreBarridoClient().get_system_status_report()
        if status.status_code == 200:
            blocked_date = status.json(object_hook=datetime_parser)
            diff = datetime.datetime.now() - blocked_date['last_blocked_accounts_database_datetime']
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            if hours > 24:
                ret.append("La tabla de Bajas de Servicio y Cuentas Cerradas está desactualizada!")
        else:
            ret.append("No fue posible validar la fecha de Bajas de Servicio y Cuentas Cerradas")

        return ret

    def get_redirect_url(self, *args, **kwargs):
        preconditions_messages = self.verify_preconditions()
        if len(preconditions_messages) > 0:
            for m in preconditions_messages:
                messages.add_message(self.request, messages.ERROR, m)
        else:
            active_wallet_process = ActiveWalletProcess.objects.create(user=self.request.user)
            if active_wallet_process:
                messages.add_message(self.request, messages.SUCCESS, "Proceso en estado {}".format(
                    active_wallet_process.get_status_display()
                ))
            else:
                messages.add_message(self.request, messages.ERROR, "No fue posible generar la cartera activa")
        return reverse_lazy("active_wallet_process_list")
