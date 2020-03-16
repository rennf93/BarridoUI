from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseServerError
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from cadetep.cadetep import CadetePClient
from cadetep.errors import ManualCashinError
from cadetep.forms import ManualCashinCreateForm
from core.models import ManualCashin


class ManualCashinListView(ListView):
    model = ManualCashin
    permission_required = 'core.manual_cashin_access'
    template_name = 'cadetep/manualcashins.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manualcashins'] = ManualCashin.objects.all()
        return context


class ManualCashinCreateView(CreateView):
    model = ManualCashin
    permission_required = 'core.manual_cashin_create'
    template_name = 'cadetep/manualcashins_create.html'
    form_class = ManualCashinCreateForm

    def post(self, request, *args, **kwargs):
        manual_cashin_dic = request.POST.dict()
        file = request.FILES['cashin_file']
        tenant = manual_cashin_dic['tenant']
        channel = manual_cashin_dic['channel']
        agreement = manual_cashin_dic['agreement']
        agreement_type = manual_cashin_dic['agreement_type']

        try:
            with transaction.atomic():
                ManualCashin(tenant=tenant, channel=channel, agreement=agreement, agreement_type=agreement_type,
                             cashin_file=file.name, user=request.user).save()

                cadetep_client = CadetePClient()
                response = cadetep_client.manual_input(file, agreement, request.user)

                if response.status_code < 200 or response.status_code >= 300:
                    messages.add_message(self.request, messages.ERROR, "No se pudo procesar el archivo!")
                    raise ManualCashinError("No se pudo enviar el archivo!")
        except ManualCashinError:
            pass

        return HttpResponseRedirect(reverse_lazy("manualcashins"))

    @staticmethod
    def get_channels(request, qs=None):
        result = {}

        if 'tenant' in request.GET:
            cadetep_client = CadetePClient()
            response = cadetep_client.get_channels(request.GET['tenant'])
            if response.ok:
                result = response.json()

        return JsonResponse(result)

    @staticmethod
    def get_agreements(request, qs=None):
        result = {}

        if 'tenant' in request.GET and 'channel' in request.GET:
            cadetep_client = CadetePClient()
            response = cadetep_client.get_agreements(request.GET['tenant'], request.GET['channel'])
            if response.ok:
                result = response.json()

        return JsonResponse(result)

