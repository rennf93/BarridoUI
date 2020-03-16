import uuid
import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.urls import reverse


def generate_dbname():
    return uuid.uuid4().hex


def upload_path(obj, filename):
    # filename = "{}.csv".format(datetime.datetime.now().strftime("%m-%d-%y-%H%M%S"))
    return "results/{}".format(filename)


class DateTimeBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Snapshot(DateTimeBase):
    STATUS = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("downloading", "Downloading"),
        ("cancelled", "Cancelled"),
        ("finished", "Finished"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dump = models.FileField(blank=True, null=True)
    generate = models.BooleanField(default=True)
    status = models.CharField(choices=STATUS, max_length=20, default="pending")

    class Meta:
        verbose_name = "Snapshot"
        verbose_name_plural = "4. Snapshots"

    def __str__(self):
        return "snapshot - {}".format(self.created_at)


class SnapshotRestore(DateTimeBase):
    STATUS = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("finished", "Finished"),
    )

    DATABASE_STATUS = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE)
    database_name = models.CharField(max_length=50, default=generate_dbname, editable=False)
    database_status = models.CharField(choices=DATABASE_STATUS, max_length=20, default="pending")
    status = models.CharField(choices=STATUS, max_length=20, default="pending")

    class Meta:
        verbose_name = "Snapshot Restore"
        verbose_name_plural = "5. Snapshots Restore"

    def __str__(self):
        return "{} ({}) - {}".format(self.database_name, self.database_status, self.created_at)


class ActiveWallet(DateTimeBase):
    STATUS = (
        ("pending", "Pendiente"),
        ("processing", "Procesando"),
        ("finished", "Terminado"),
        ("error", "Error"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    salary = models.ForeignKey("Salary", on_delete=models.CASCADE)
    focusgroup = models.ForeignKey("FocusGroup", on_delete=models.CASCADE, null=True, blank=True)
    result = models.FileField(verbose_name="Cartera de Debito Directo", upload_to=upload_path, blank=True, null=True,
                              editable=False)
    resultCollection = models.FileField(verbose_name="Cartera de Cobranzas a Clientes", upload_to=upload_path,
                                        blank=True, null=True,
                                        editable=False)
    resultReno = models.FileField(verbose_name="Cartera de Renos", upload_to=upload_path, blank=True, null=True,
                                  editable=False)
    resultFeesCharged = models.FileField(verbose_name="Cuotas cobradas", upload_to=upload_path, blank=True, null=True,
                                         editable=False)
    resultMifosCa = models.FileField(verbose_name="Cartera Activa Mifos", upload_to=upload_path, blank=True, null=True,
                                         editable=False)
    snapshot_restore = models.ForeignKey(SnapshotRestore, null=True, on_delete=models.SET_NULL)
    status = models.CharField(choices=STATUS, max_length=20, default="pending")
    status_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Cartera Activa"
        verbose_name_plural = "6. Carteras Activas"
        permissions = (
            ('active_wallet_access', 'Can access active wallet'),
        )
        

    def __str__(self):
        return "cartera activa - {}".format(self.created_at)


class ActiveWalletReport(DateTimeBase):
    STATUS = (
        ("pending", "Pendiente"),
        ("generating", "Generando"),
        ("processing", "Procesando"),
        ("finished", "Terminado"),
        ("error", "Error")
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    salary = models.ForeignKey("Salary", on_delete=models.CASCADE)
    focusgroup = models.ForeignKey("FocusGroup", on_delete=models.CASCADE, null=True, blank=True)
    origin_report = models.FileField(verbose_name="Reporte con datos origen", upload_to=upload_path, blank=True,
                                     null=True,
                                     editable=True, validators=[FileExtensionValidator(allowed_extensions=['zip'])])
    result = models.FileField(verbose_name="Cartera de Debito Directo", upload_to=upload_path, blank=True, null=True,
                              editable=False)
    resultCollection = models.FileField(verbose_name="Cartera de Cobranzas a Clientes", upload_to=upload_path,
                                        blank=True, null=True,
                                        editable=False)
    resultReno = models.FileField(verbose_name="Cartera de Renos", upload_to=upload_path, blank=True, null=True,
                                  editable=False)
    resultFeesCharged = models.FileField(verbose_name="Cartera Cuotas Cobradas", upload_to=upload_path, blank=True,
                                         null=True,
                                         editable=False)
    resultMifosCa = models.FileField(verbose_name="Cartera Activa Mifos", upload_to=upload_path, blank=True,
                                         null=True,
                                         editable=False)
    status = models.CharField(choices=STATUS, max_length=20, default="pending")
    status_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Cartera Activa"
        verbose_name_plural = "8. Carteras Activas x Reporte"
        permissions = (
            ('active_wallet_access', 'Can access active wallet'),
        )

    def __str__(self):
        return "cartera activa - {}".format(self.created_at)


class ActiveWalletProcess(DateTimeBase):
    STATUS = (
        ("pending", "Pendiente 1/6"),
        ("mambu_generating", "Generando Snapshot 2/6"),
        ("downloading", "Descargando Snapshot 3/6"),
        ("restoring", "Restaurando Snapshot 4/6"),
        ("wallet_generating", "Generando Cartera 5/6"),
        ("finished", "Terminado"),
        ("failure", "Fallido"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    active_wallet = models.ForeignKey(ActiveWallet, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, max_length=20, default="pending")
    failure_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Proceso de Cartera Activa"
        verbose_name_plural = "7. Procesos de Carteras Activas"
        permissions = (
            ('active_wallet_access', 'Can access active wallet'),
        )

    def __str__(self):
        return "proceso de cartera activa - {}".format(self.created_at)

    def change_status(self, status, failure_reason=None):
        self.status = status
        if failure_reason:
            self.failure_reason = failure_reason
        self.save()

    @property
    def last_process_time(self):
        last_process = self._meta.model.objects.filter(status="finished").last()
        if last_process:
            return last_process.updated_at - last_process.created_at
        return

    @property
    def estimated_finish_date(self):
        if self.last_process_time:
            return self.created_at + self.last_process_time
        return


class Salary(DateTimeBase):
    def __str__(self):
        return "{}-{}".format(self.salary_csv.name, self.created_at)

    class Meta:
        verbose_name = "Sueldo"
        verbose_name_plural = "1. Sueldos"

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    salary_csv = models.FileField(
        help_text="El archivo debe tener dos columnas separadas por 'punto-y-coma': DNI;Sueldo")


class FocusGroup(DateTimeBase):
    def __str__(self):
        return "{}-{}".format(self.focusgroup_csv.name, self.created_at)

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "2. Grupos"

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    focusgroup_csv = models.FileField(help_text="El archivo debe tener dos columnas separadas por 'coma': DNI,Grupo")


class CollectionCycle(DateTimeBase):
    def __str__(self):
        return "{} middle {} to {}".format(self.start_date, self.middle_date, self.end_date)

    class Meta:
        verbose_name = "Ciclo Cobranza"
        verbose_name_plural = "3. Ciclos Cobranza"

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    start_process_date = models.DateField(verbose_name="Fecha Inicio de Proceso", null=True, blank=False, unique=True,
                                          help_text="Indica el inicio del proceso (fecha de la 'foto')")
    start_date = models.DateField(verbose_name="Fecha Inicio", null=False, blank=False, unique=True,
                                  help_text="Indica el inicio del ciclo de cobranza (inclusiva)")
    middle_date = models.DateField(verbose_name="Fecha Inicio 2da quincena", null=False, blank=False,
                                   help_text="Indica el comienzo de la segunda quincena (inclusiva)")
    end_date = models.DateField(verbose_name="Fecha Fin", null=False, blank=False, unique=True,
                                help_text="Indica el fin del ciclo de cobranza (exclusiva, debe coincidir con la fecha de inicio del mes siguiente)")
    result = models.FileField(verbose_name="Cartera Inicial", upload_to=upload_path, blank=True, null=True,
                              editable=False)


class GenericCashin(DateTimeBase):
    STATUS = (
        ("pending", "Pendiente"),
        ("pending_approve", "Pendiente Aprobación"),
        ("approved", "Aprobado"),
        ("error", "Error"),
        ("finished", "Enviado"),
    )

    # CONSUMER_USERNAME = (
    #    ("mambu-welp-ar", "mambu-welp-ar"),
    # )

    CONSUMER_USERNAME = [
        (None, "Seleccione..."),
        ("mambu-welp-ar", "mambu-welp-ar"),
        ("mambu-creditoalrio-ar", "mambu-creditoalrio-ar"),
        ("mambu-welp-es", "mambu-welp-es")
    ]

    def __str__(self):
        return "generic_cashin_{}".format(self.created_at)

    class Meta:
        verbose_name = "Cashin Generico"
        verbose_name_plural = "9. Cashin Genericos"

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    approved_user = models.ForeignKey(get_user_model(), related_name='approved_user', on_delete=models.CASCADE,
                                      editable=False, null=True)
    approved_at = models.DateTimeField(auto_now=False, editable=False, null=True)
    consumer_username = models.CharField(choices=CONSUMER_USERNAME, max_length=50, default=None,
                                         editable=True, null=True)
    cashin_csv = models.FileField(verbose_name="Cashin", upload_to=upload_path, blank=False, null=False,
                                  help_text="Archivo CSV: Fecha_Cobro,Nro_Operacion,Nombre del titular de la cuenta,DNI,Id_Transaccion_Banco,Importe,Estado,CBU,Banco")
    bank = models.CharField(max_length=20, editable=False, null=True)
    status = models.CharField(choices=STATUS, max_length=20, default="pending", editable=False)
    resume = models.TextField(editable=False)
    comment = models.CharField(verbose_name="Motivo", max_length=500, null=True)
    error_detail = models.TextField(editable=False)

    def change_status(self, status, failure_reason=None, user=None):
        self.status = status
        if status == 'approved':
            self.approved_at = datetime.datetime.now()
            self.approved_user = user
        if failure_reason:
            self.failure_reason = failure_reason
        self.save()


class ManualCashin(DateTimeBase):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tenant = models.CharField(max_length=50, default=None, editable=True, null=True)
    cashin_file = models.FileField(verbose_name="Cashin", upload_to=upload_path, blank=False, null=False)
    channel = models.CharField(max_length=50, default=None, editable=True, null=True)
    agreement = models.CharField(max_length=50, default=None, editable=True, null=True)
    agreement_type = models.CharField(max_length=50, default=None, editable=True, null=True)

    def __str__(self):
        return "manual_cashin_{}".format(self.created_at)

    class Meta:
        verbose_name = "Cashin Manual"
        verbose_name_plural = "Cashins Manual"
        permissions = (
            ('manual_cashin_access', 'Can access Manual Cashin'),
            ('manual_cashin_create', 'Can create Manual Cashin')
        )


class CashIORightsSupport(models.Model):
    class Meta:
        managed = False

        permissions = (
            ('cashio_access', 'Can access CashIO'),
            ('bank_access', 'Can access Bank Config'),
            ('active_wallet_access', 'Can access Carteras Activas'),
            ('active_wallet_add_access', 'Can add Carteras Activas'),
            ('buckets_strategy_access_debito_directo', 'Can access [debito_directo] Estrategias de Buckets'),
            ('buckets_strategy_access_reno', 'Can access [reno] Estrategias de Buckets'),
            ('buckets_strategy_access_cobranza_espana', 'Can access [espana] Estrategias de Buckets'),
            ('buckets_strategy_access_cobranza_mexico', 'Can access [mexico] Estrategias de Buckets'),
            ('buckets_strategy_access_cobranza_atencion_cliente',
             'Can access [cobranza_atencion_cliente] Estrategias de Buckets'),
            ('strategy_exec_access_debito_directo', 'Can access [debito_directo] Ejecuciones'),
            ('strategy_exec_access_reno', 'Can access [reno] Ejecuciones'),
            ('strategy_exec_access_cobranza_espana', 'Can access [espana] Ejecuciones'),
            ('strategy_exec_access_cobranza_mexico', 'Can access [mexico] Ejecuciones'),
            ('strategy_exec_access_cobranza_atencion_cliente', 'Can access [cobranza_atencion_cliente] Ejecuciones'),
            ('strategy_exec_add_access_debito_directo', 'Can add [debito_directo] Ejecuciones'),
            ('strategy_exec_add_access_reno', 'Can add [reno] Ejecuciones'),
            ('strategy_exec_add_access_cobranza_espana', 'Can add [espana] Ejecuciones'),
            ('strategy_exec_add_access_cobranza_mexico', 'Can add [mexico] Ejecuciones'),
            ('strategy_exec_add_access_cobranza_atencion_cliente', 'Can add [cobranza_atencion_cliente] Ejecuciones'),
            ('active_wallet_download_access', 'Can download Cartera Activa Debito Directo'),
            ('active_wallet_download_collection_access', 'Can download Cartera Activa Cobranzas'),
            ('active_wallet_download_access_cobranza_espana', 'Can download Cartera de España'),
            ('active_wallet_download_access_cobranza_mexico', 'Can download Cartera de México'),
            ('active_wallet_download_access_reno', 'Can download Cartera de Renos'),
            ('active_wallet_download_fees_charged', 'Can download Cartera de Cuotas Cobradas' ),
            ('active_wallet_download_mifos_access', 'Can download Cartera de Mifos'),
            ('agent_data_access', 'Can access Datos Agentes Pago'),
            ('outputs_strategy_access_debito_directo', 'Can access [debito_directo] Outputs Strategies'),
            ('outputs_strategy_access_reno', 'Can access [reno] Outputs Strategies'),
            ('outputs_strategy_access_cobranza_espana', 'Can access [espana] Outputs Strategies'),
            ('outputs_strategy_access_cobranza_mexico', 'Can access [mexico] Outputs Strategies'),
            ('outputs_strategy_access_cobranza_atencion_cliente',
             'Can access [cobranza_atencion_cliente] Outputs Strategies'),
            ('paying_agents_strategy_access_debito_directo', 'Can access [debito_directo] Estrategias Bancos'),
            ('paying_agents_strategy_access_reno', 'Can access [reno] Estrategias Bancos'),
            ('paying_agents_strategy_access_cobranza_espana', 'Can access [cobranza_espana] Estrategias Bancos'),
            ('paying_agents_strategy_access_cobranza_mexico', 'Can access [mexico] Estrategias Bancos'),
            ('paying_agents_strategy_access_cobranza_atencion_cliente',
             'Can access [cobranza_atencion_cliente] Estrategias Bancos'),
            ('data_source_reader_settings_access_debito_directo',
             'Can access [debito_directo] Data Source Reader Settings'),
            ('data_source_reader_settings_access_reno', 'Can access [reno] Data Source Reader Settings'),
            ('data_source_reader_settings_access_cobranza_espana',
             'Can access [cobranza_espana] Data Source Reader Settings'),
            ('data_source_reader_settings_access_cobranza_mexico',
             'Can access [cobranza_mexico] Data Source Reader Settings'),
            ('data_source_reader_settings_access_cobranza_atencion_cliente',
             'Can access [cobranza_atencion_cliente] Data Source Reader Settings'),
        )


class CadeteRightsSupport(models.Model):
    class Meta:
        managed = False

        permissions = (
            ('cadete_access', 'Can access Cadete'),
            ('cadete_configuration_edit', 'Can edit Configuraciones'),
            ('cadete_operations_edit', 'Can edit Operaciones'),
        )


class MiddlewareRightsSupport(models.Model):
    class Meta:
        managed = False

        permissions = (
            ('middleware_access', 'Can access Middleware'),
            ('cashin_process_access', 'Can access Cashin Process Status'),
            ('cashout_summaries_access', 'Can access Cashout Summaries'),
            ('mw_companies_access', 'Can access Companies'),
            ('cashin_binnacle_summaries_access', 'Can access Cashin Bitacora'),
        )


class AdminRightsSupport(models.Model):
    class Meta:
        managed = False

        permissions = (
            ('admin_access', 'Can access Administration'),
            ('cashin_process_approve', 'Can approve Cashin Generico'),
        )


class CompanyAccessRightsSupport(models.Model):
    class Meta:
        managed = False

        permissions = (
            ('company_wenance', 'Belongs to wenance'),
            ('company_car', 'Belongs to Créditos Al Río')
        )


class BondiRightsSupport(models.Model):
    class Meta:
        managed = False

        permissions = (
            ('bondi_access', 'Can access Bondi'),
            ('bondi_topics_edit', 'Can edit Topics'),
        )
