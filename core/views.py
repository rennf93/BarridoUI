from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.models import Snapshot, GenericCashin
from django.contrib import messages
from django.urls import reverse_lazy


class GenerateSnapshotAdminView(LoginRequiredMixin, RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'admin:core_snapshot_changelist'

    def get_redirect_url(self, *args, **kwargs):
        if Snapshot.objects.filter(status__in=("processing", "pending")).exists():
            messages.add_message(self.request, messages.ERROR, "Ya existe un proceso de snapshot")
        else:
            Snapshot.objects.create(user=self.request.user)
            messages.add_message(self.request, messages.INFO, "El snapshot se estara generando previamente.")
        return super(GenerateSnapshotAdminView, self).get_redirect_url(*args, **kwargs)


class DownloadSnapshotAdminView(LoginRequiredMixin, RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'admin:core_snapshot_changelist'

    def get_redirect_url(self, *args, **kwargs):
        if Snapshot.objects.filter(status="downloading").exists():
            messages.add_message(self.request, messages.ERROR, "Ya existe un proceso de descarga")
        else:
            Snapshot.objects.create(user=self.request.user, generate=False)
            messages.add_message(self.request, messages.INFO, "El snapshot se estara descargando previamente")
        return super(DownloadSnapshotAdminView, self).get_redirect_url(*args, **kwargs)


class GenericCashinAdminView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    permission_required = 'core.cashin_process_approve'
    permanent = False
    query_string = True
    pattern_name = 'admin:core_genericcashin_changelist'

    def get_redirect_url(self, *args, **kwargs):
        generic_cashin_id = kwargs.get('generic_cashin_id')
        generic_cashin = GenericCashin.objects.get(id=generic_cashin_id)    
        generic_cashin.change_status("approved", user=self.request.user)
        kwargs.pop('generic_cashin_id', None)
        return super(GenericCashinAdminView, self).get_redirect_url(*args, **kwargs)

