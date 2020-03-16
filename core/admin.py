import pandas
from django.contrib import admin
from celery.utils.log import get_task_logger
from .models import Snapshot, SnapshotRestore, ActiveWallet, Salary, FocusGroup, ActiveWalletProcess, CollectionCycle, \
    GenericCashin, ActiveWalletReport
from .views import GenerateSnapshotAdminView, DownloadSnapshotAdminView, GenericCashinAdminView
from django.urls import path, reverse
from django import forms
from django.utils.html import format_html
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings

logger = get_task_logger(__name__)
current_username = ""


class SnapshotAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_filter = ('status', )
    readonly_fields = ("user", "status", "dump")
    exclude = ("generate", )
    search_fields = ('user__email', 'user__first_name', 'user__last_name', )
    change_list_template = "change_list_snapshot.html"

    def get_urls(self):
        urls = [
            path('generate/', GenerateSnapshotAdminView.as_view(), name="generate_snapshot"),
            path('download/', DownloadSnapshotAdminView.as_view(), name="download_snapshot"),
        ]
        urls += super().get_urls()
        return urls

    def has_add_permission(self, request):
        return False


class SnapshotRestoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'snapshot', 'status', 'database_name', 'database_status', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_filter = ('status', )
    readonly_fields = ("user", "status", "database_status")
    search_fields = ('user__email', 'user__first_name', 'user__last_name', )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(SnapshotRestoreAdmin, self).save_model(request, obj, form, change)


class ActiveWalletAdminForm(forms.ModelForm):
    class Meta:
        model = ActiveWallet
        fields = '__all__'

    def clean_snapshot_restore(self):
        value = self.cleaned_data.get("snapshot_restore")
        if self.Meta.model.objects.filter(snapshot_restore=value).exists():
            raise forms.ValidationError("Ya se ha generado una cartera activa para este snapshot")
        return value


class ActiveWalletAdmin(admin.ModelAdmin):
    form = ActiveWalletAdminForm
    list_display = ('user', 'snapshot_restore', 'status', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_filter = ('status', )
    readonly_fields = ("user", "status", "status_description", "result", "resultCollection", "resultReno", "resultFeesCharged", "resultMifosCa")
    search_fields = ('user__email', 'user__first_name', 'user__last_name', )

    def get_form(self, request, obj=None, **kwargs):
        form = super(ActiveWalletAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['snapshot_restore'].queryset = SnapshotRestore.objects.filter(
            database_status='active')
        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(ActiveWalletAdmin, self).save_model(request, obj, form, change)


class ActiveWalletReportAdmin(admin.ModelAdmin):
    form = ActiveWalletAdminForm
    list_display = ('user', 'status', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_filter = ('status', )
    readonly_fields = ("user", "status", "result", "resultCollection", "resultReno", "resultFeesCharged", "resultMifosCa")
    search_fields = ('user__email', 'user__first_name', 'user__last_name', )

    def get_form(self, request, obj=None, **kwargs):
        form = super(ActiveWalletReportAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(ActiveWalletReportAdmin, self).save_model(request, obj, form, change)


class SalaryAdmin(admin.ModelAdmin):
    exclude = ('user', )
    list_display = ('user', 'salary_csv',  'created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(SalaryAdmin, self).save_model(request, obj, form, change)


class FocusGroupAdmin(admin.ModelAdmin):
    exclude = ('user', )
    list_display = ('user', 'focusgroup_csv',  'created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(FocusGroupAdmin, self).save_model(request, obj, form, change)


class CollectionCycleAdmin(admin.ModelAdmin):
    exclude = ('user', )
    list_display = ('start_process_date', 'start_date', 'middle_date', 'end_date', 'result', 'user', 'created_at', 'updated_at')
    ordering = ('-start_date',)

    fieldsets = (
            (None, {
                'fields': ('start_process_date', 'start_date', 'middle_date', 'end_date')
            }),
            ('Advanced options', {
                'classes': (),
                'fields': (),
            })
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(CollectionCycleAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['start_process_date',]
        else:
            return []


class ActiveWalletProcessAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_filter = ('status', )
    readonly_fields = ("user", "status", "failure_reason")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(ActiveWalletProcessAdmin, self).save_model(request, obj, form, change)


class GenericCashinForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GenericCashinForm, self).__init__(*args, **kwargs)
        if settings.APP_COMPANY == 'wenance':
            self.fields['consumer_username'].choices = [
                (None, "Seleccione..."),
                ("mambu-welp-ar", "mambu-welp-ar"),
                ("mambu-welp-es", "mambu-welp-es")
            ]
        elif settings.APP_COMPANY == 'car':
            self.fields['consumer_username'].choices = [
                (None, "Seleccione..."),
                ("mambu-creditoalrio-ar", "mambu-creditoalrio-ar")
            ]
        else:
            self.fields['consumer_username'].choices = []

    def clean_cashin_csv(self):
        value = self.cleaned_data.get("cashin_csv")
        logger.info("validating cashin csv file {}".format(value))
        req_colums = ["Fecha_Cobro", "Nro_Operacion", "DNI", "Id_Transaccion_Banco", "Importe", "Estado", "CBU", "Banco"]

        cg_csv = pandas.read_csv(value, delimiter=",", quotechar='"', index_col=False, header=0, decimal=".")
        bank_group = cg_csv.groupby(['Banco']).Importe.sum()

        if bank_group.size != 1:
            raise forms.ValidationError("Verifique el formato del archivo, solo puede asignarse un Banco")

        head_cols = cg_csv.head(0).columns
        format_ok = all(item in head_cols for item in req_colums)
        if not format_ok:
            raise forms.ValidationError("Verifique el formato del archivo, debe contener todas las columnas indicadas")
        return value


class AuthorDelete(DeleteView):
    model = GenericCashin
    success_url = reverse_lazy('authors')


class GenericCashinAdmin(admin.ModelAdmin):
    form = GenericCashinForm
    exclude = ('user', )
    list_display = ('created_at', 'user', 'status', 'approved_user', 'approved_at', 'cashin_csv', 'resume', 'generic_cashin_actions')
    ordering = ('-created_at',)

    def get_actions(self, request):
        actions = super(GenericCashinAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_urls(self):
        urls = [
            path('approve/<str:generic_cashin_id>', GenericCashinAdminView.as_view(), name="generic_cashin_approve"),            
            path('approve/<str:generic_cashin_id>', GenericCashinAdminView.as_view(), name="generic_cashin_approve"),            
        ]
        urls += super().get_urls()
        return urls
 
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(GenericCashinAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if obj.status in ['pending', 'pending_approve']:
            obj.delete()
        else:     
            storage = messages.get_messages(request)
            storage.used = True
            messages.error(request, "Solo se pueden borrar procesos Pendientes")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['cashin_csv', 'bank', 'comment', 'consumer_username', 'user', 'approved_user', 'approved_at', 'error_detail',]
        else:
            return []

    def generic_cashin_actions(self, obj):                
        if obj.status == 'pending_approve' and self.current_user.has_perm('core.cashin_process_approve'):
            if self.current_user.username == obj.user.username:
                return format_html('<font color="red">Debe aprobar otro Usuario</font>')
            return format_html(
                '<a class="button" href="{}">Aprobar</a>&nbsp;',
                reverse('admin:generic_cashin_approve', args=[obj.pk]),
            )
        return ''

    def __init__(self, model, admin_site): 
        self.current_user = None
        super().__init__(model, admin_site)

    def get_queryset(self, request):
        self.current_user = request.user      
        return super().get_queryset(request)

    generic_cashin_actions.short_description = 'Acciones'
    generic_cashin_actions.allow_tags = True


admin.site.register(Snapshot, SnapshotAdmin)
admin.site.register(SnapshotRestore, SnapshotRestoreAdmin)
admin.site.register(ActiveWallet, ActiveWalletAdmin)
admin.site.register(ActiveWalletProcess, ActiveWalletProcessAdmin)
admin.site.register(Salary, SalaryAdmin)
admin.site.register(FocusGroup, FocusGroupAdmin)
admin.site.register(CollectionCycle, CollectionCycleAdmin)
admin.site.register(GenericCashin, GenericCashinAdmin)
admin.site.register(ActiveWalletReport, ActiveWalletReportAdmin)
