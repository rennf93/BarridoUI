import datetime

from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__name__)

TEST_COLUMNS = """
    Id|Estado|Estado_Mambu|Cliente_en_Gest_Especial|Gestor|Status|Sucursal_Prestamo|Centro_Prestamo|AyN|DNI|NombreLinea|fecha_otorgado|Capital|Plazo|ValorCuota|Ultimo_Vto|',
              'FecUltCuotaImpaga|Proximo_Vto|fecha_1Vto|FecUltCuotaPagaMesAnt|Mes_cepa|fecha_ultimo_pago_parcial|DiasAtraso|MoraCuotas|PunitoriosAdeudados|CargosAdeudados|CantidadCuotasAdeudadas|SaldoCuotasNoVencidas|SaldoExigible|CBU|',
              'Gestion Cobranza|ID_Op_CRM|Promesa_Pago_Desc|Promesa_Pago_Vencimiento|Promesa_Pago_Monto|Promesa_Pago_Dias_Vencer|CBU_Pred|email|celular|telefono_alternativo|Cliente_Cuit|SaldoDeCapitalAdeudado|SaldoDeInteres|InteresDevengado|',
              'SaldoDeCargo|SaldoDePenalizacion|PrincipalPendiente|InteresPendiente|CargosPendientes|PenalizacionPendiente|TotalPagado|PrincipalPagado|InteresPagado|CargosPagados|PenalizacionPagada|Id_Cliente|Id_Solicitud|Total_Cta_Recaudadora|',
              'Cargos_y_Penalidades|Total_a_Barrer|Total_a_Barrer_anterior|Bucket|K_mas_I|Sueldo|Grupo|Fecha_cartera|Con_cobro_2da_quincena|Monto_cobranza_inicial|Dias_atraso_inicial|Estado_inicial|Fecha_cartera_inicial|Tipo_ultimo_barrido|',
              'Banco_utlimo_barrido|PayingAgentBlockedRules|Fecha_ult_deposito|Dias_ult_debito_banco|Calle - Cliente|Nro - Cliente|Provincia - Cliente|CP - Cliente
              """

TEST_COLUMNS_DOS = """
        Id|Estado|Estado_Mambu|Cliente_en_Gest_Especial|Gestor|Status|Sucursal_Prestamo|Centro_Prestamo|AyN|DNI|NombreLinea|fecha_otorgado|Capital|Plazo|ValorCuota|Ultimo_Vto|FecUltCuotaImpaga|Proximo_Vto|fecha_1Vto|FecUltCuotaPagaMesAnt|Mes_cepa|fecha_ultimo_pago_parcial|DiasAtraso|MoraCuotas|PunitoriosAdeudados|CargosAdeudados|CantidadCuotasAdeudadas|SaldoCuotasNoVencidas|SaldoExigible|CBU|Gestion Cobranza|ID_Op_CRM|Promesa_Pago_Desc|Promesa_Pago_Vencimiento|Promesa_Pago_Monto|Promesa_Pago_Dias_Vencer|CBU_Pred|email|celular|telefono_alternativo|Cliente_Cuit|SaldoDeCapitalAdeudado|SaldoDeInteres|InteresDevengado|SaldoDeCargo|SaldoDePenalizacion|PrincipalPendiente|InteresPendiente|CargosPendientes|PenalizacionPendiente|TotalPagado|PrincipalPagado|InteresPagado|CargosPagados|PenalizacionPagada|Id_Cliente|Id_Solicitud|Total_Cta_Recaudadora|Cargos_y_Penalidades|Total_a_Barrer|Total_a_Barrer_anterior|Bucket|K_mas_I|Sueldo|Grupo|Fecha_cartera|Con_cobro_2da_quincena|Monto_cobranza_inicial|Dias_atraso_inicial|Estado_inicial|Fecha_cartera_inicial|Tipo_ultimo_barrido|Banco_utlimo_barrido|PayingAgentBlockedRules|Fecha_ult_deposito|Dias_ult_debito_banco|Direccion|Provincia - Cliente
        """


def jasper_columns():
    return TEST_COLUMNS_DOS


def update_with_salary_query(database_name, ca_table, salary_table):
    return \
        f'UPDATE {database_name}.{ca_table} ca ' \
            f'JOIN {database_name}.{salary_table} cs ' \
            f'ON cs.dni = ca.dni ' \
            f'SET ca.sueldo = cs.sueldos;'


def update_with_xselling_query(database_name, ca_table, xselling_table):
    return \
        f'UPDATE {database_name}.{ca_table} ca ' \
            f'JOIN {database_name}.{xselling_table} csx ' \
            f'ON csx.externalId = ca.Id_Cliente ' \
            f'SET ca.Deuda_crossselling = csx.totalDue;'


def cartera_activa_database_name():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    db_name = settings.MYSQL_WENANCE_DEV if getattr(settings, "MYSQL_WENANCE_DEV",
                                                    False) else f"wallet-dump-{timestamp}"
    return db_name


def cartera_clientes_table_name():
    return f"cartera_clientes_report"

