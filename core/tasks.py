import linecache
import os
import io
import requests
import datetime
import pandas
import zipfile
import re
import gzip
import time
import gc
import linecache
from pandas.tseries.offsets import BMonthEnd, BMonthBegin, BDay
from datetime import date
from subprocess import Popen, PIPE
from celery.utils.log import get_task_logger
from celery.decorators import task
# from celery.task.schedules import crontab
from celery.task import Task, PeriodicTask
from core.models import (Snapshot, SnapshotRestore, ActiveWallet, ActiveWalletProcess, Salary, FocusGroup,
                         CollectionCycle, GenericCashin, ActiveWalletReport)
from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse
from django.contrib.auth.models import User
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy_utils.functions import database_exists, create_database, drop_database
from core.notification import NotificationClient
from django.db.models import signals
from core import signals as core_signals
from core.services.sql_service import SqlService
from core.utils import TempSignalDisconnect
from middleware.core_middleware import CoreMiddlewareClient
from core.core_barrido import CoreBarridoClient
from core.mifos_client import MifosClient
from core.services.cartera_activa_service import CarteraActivaService
from bondi.bondi_client import BondiClient
from core.parsers import datetime_parser

logger = get_task_logger(__name__)


@task()
def generate_snapshot_task(snapshot_id, callback):
    logger.info("starting generate_snapshot_task id={}".format(snapshot_id))

    snapshot = Snapshot.objects.get(id=snapshot_id)
    headers = {
        "Authorization": "Basic {}".format(getattr(settings, "MAMBU_API_AUTHORIZATION")),
        "Content-Type": "application/json"
    }
    payload = {
        "callback": callback
    }
    url = getattr(settings, "MAMBU_API_GENERATE_SNAPSHOT")
    logger.info("generating mambu backup:")
    logger.info("headers: {}".format(headers))
    logger.info("url: {}".format(url))
    logger.info("payload: {}".format(payload))
    response = requests.post(url, headers=headers, json=payload)
    logger.info("response: {}".format(response.content))
    logger.info("status code: {}".format(response.status_code))
    snapshot.status = "processing" if response.status_code == 200 else "cancelled"
    snapshot.save()


@task()
def download_snapshot_task(snapshot_id):
    logger.info("starting download_snapshot_task id={}, waiting...".format(snapshot_id))
    time.sleep(5)
    logger.info("now yes, starting download_snapshot_task id={}".format(snapshot_id))

    snapshot = Snapshot.objects.get(id=snapshot_id)
    snapshot.status = "downloading"
    snapshot.save()

    barrido_client = CoreBarridoClient()
    status = barrido_client.get_system_status_report()
    if status.status_code == 200:
        blocked_date = status.json(object_hook=datetime_parser)
        diff = datetime.datetime.now() - blocked_date['last_blocked_accounts_database_datetime']
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        if hours > 24:
            NotificationClient().send_generic("AVISO: Se esta generando una Cartera Activa con las bajas de servicio desactualizadas (mas de 24hs). (Snapshot: {})".format(snapshot_id))
    else:
        NotificationClient().send_generic("AVISO: El proceso de Cartera Activa no pudo verificar la antigüedad de los datos de bajas de servicios (Snapshot: {}). Continuando proceso.".format(snapshot_id))

    headers = {
        "Authorization": "Basic {}".format(getattr(settings, "MAMBU_API_AUTHORIZATION")),
        "Content-Type": "application/json"
    }
    url = getattr(settings, "MAMBU_API_ENDPOINT_BACKUP")
    logger.info("downloading mambu backup:")
    logger.info("headers: {}".format(headers))
    logger.info("url: {}".format(url))
    response = requests.get(url, headers=headers, stream=True)
    logger.info("status code: {}".format(response.status_code))
    logger.info("response headers: {}".format(response.headers))
    local_filename = "dump-{}.zip".format(datetime.datetime.now().strftime("%m-%d-%y-%H%M%S"))
    os.makedirs(getattr(settings, "MEDIA_ROOT"), exist_ok=True)
    with open(os.path.join(getattr(settings, "MEDIA_ROOT"), local_filename), 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
        snapshot.dump.name = local_filename
        snapshot.status = "finished"
        snapshot.save()
    logger.info("download complete!")


@task()
def snapshot_finish_task():
    logger.info("starting snapshot_finish_task")

    try:
        keep_qty = int(getattr(settings, "SNAPSHOTS_TO_KEEP", 10))
        logger.info("snapshots to keep: {}".format(keep_qty))

        logger.info("deleting Snapshot")
        logger.info("Snapshot count before deletion: {}".format(Snapshot.objects.all().count()))
        keep = Snapshot.objects.all().order_by('-created_at')[:keep_qty].values_list("id", flat=True)
        logger.info("Snapshot list to deletion: {}".format(keep))
        Snapshot.objects.exclude(pk__in=list(keep)).delete()
        logger.info("Snapshot count after deletion: {}".format(Snapshot.objects.all().count()))
    except Exception as e:
        logger.info("error snapshot_finish_task: {}".format(e))
        logger.exception(e)
        pass


@task()
def restore_snapshot_task(snapshot_restore_id):
    logger.info("starting restore_snapshot_task id={}, waiting...".format(snapshot_restore_id))
    time.sleep(5)
    logger.info("now yes, starting restore_snapshot_task id={}".format(snapshot_restore_id))

    snapshot_restore = SnapshotRestore.objects.get(id=snapshot_restore_id)
    snapshot_restore.status = "processing"
    snapshot_restore.save()
    engine = create_engine("mysql://{}:{}@{}/{}".format(
        settings.MYSQL_USER,
        settings.MYSQL_PASSWORD,
        settings.MYSQL_HOST,
        snapshot_restore.database_name
    ))
    if database_exists(engine.url):
        logger.info("db '{}' already exists, skipping process...".format(snapshot_restore.database_name))
        return

    logger.info("creating db '{}'".format(snapshot_restore.database_name))
    create_database(engine.url)
    snapshot_restore.database_status = "processing"
    snapshot_restore.save()

    logger.info("checking file exists: {}".format(snapshot_restore.snapshot.dump.path))
    exists = os.path.isfile(snapshot_restore.snapshot.dump.path)
    if exists:
        logger.info("file exists")
    else:
        logger.info("file doesn't exists")

    start = time.time()
    logger.info("unzip dump {}".format(snapshot_restore.snapshot.dump.path))
    unzip = Popen([
        "7z", "e", "-y", snapshot_restore.snapshot.dump.path,
        "-o{}/".format(settings.MEDIA_ROOT)
    ], stdout=PIPE, stderr=PIPE)
    stdout, stderr = unzip.communicate()
    logger.info(stdout)
    logger.info(stderr)
    logger.info("unzip complete in {}s".format(round(time.time() - start, 2)))
    unzip_dumpfile = "{}/{}.sql".format(settings.MEDIA_ROOT, settings.MAMBU_BACKUP_SQL_NAME)
    with open("{}/wenance_sed.sql".format(settings.MEDIA_ROOT), 'w') as sed_dumpfile:
        start = time.time()
        logger.info("start sed command gljournalentry and activity")
        dump_sed = Popen([
            "sed", "-n", "-e", "/LOCK TABLES `gljournalentry`/,/UNLOCK TABLES/d",
            "-e", "/LOCK TABLES `activity`/,/UNLOCK TABLES/!p",
            unzip_dumpfile
        ], stdout=sed_dumpfile, stderr=PIPE)
        stdout, stderr = dump_sed.communicate()
        logger.info(stdout)
        logger.info(stderr)
        logger.info("sed gljournalentry complete and activity complete in {}s".format(round(time.time() - start, 2)))

        if os.path.isfile(unzip_dumpfile):
            logger.info("removing {}".format(unzip_dumpfile))
            os.remove(unzip_dumpfile)

    with open(sed_dumpfile.name, 'r') as sed_dumpfile:

        # engine.execute("SET GLOBAL FOREIGN_KEY_CHECKS = 0")
        # engine.execute("SET GLOBAL UNIQUE_CHECKS = 0")
        # engine.execute("SET GLOBAL AUTOCOMMIT = 0")
        start = time.time()
        logger.info("processing dumpfile to mysql")
        proc = Popen([
            # "mysql", "--net-buffer-length=500M --max_allowed_packet=2G",
            "mysql", "-h{}".format(settings.MYSQL_HOST), "-u{}".format(settings.MYSQL_USER),
            "-p{}".format(settings.MYSQL_PASSWORD), snapshot_restore.database_name
        ], stdout=PIPE, stderr=PIPE, stdin=sed_dumpfile)
        stdout, stderr = proc.communicate()
        logger.info(stdout)
        logger.info(stderr)
        # engine.execute("SET GLOBAL FOREIGN_KEY_CHECKS = 1")
        # engine.execute("SET GLOBAL UNIQUE_CHECKS = 1")
        # engine.execute("SET GLOBAL AUTOCOMMIT = 1")
        if os.path.isfile(sed_dumpfile.name):
            logger.info("removing {}".format(sed_dumpfile.name))
            os.remove(sed_dumpfile.name)
    logger.info("restore complete in {}s".format(round(time.time() - start, 2)))
    snapshot_restore.status = "finished"
    snapshot_restore.database_status = "active"
    snapshot_restore.save()
    logger.info("sending notification")
    NotificationClient().send_generic("Finalizó el Restore del Snapshot id={}".format(snapshot_restore_id))
    logger.info("sending notification complete")


@task()
def snapshot_restore_finish_task():
    logger.info("starting snapshot_restore_finish_task")

    try:
        keep_restore_qty = int(getattr(settings, "SNAPSHOTS_RESTORE_TO_KEEP", 4))
        logger.info("snapshots_restore to keep: {}".format(keep_restore_qty))

        logger.info("deleting SnapshotRestore")
        logger.info("SnapshotRestore count before deletion: {}".format(SnapshotRestore.objects.all().count()))
        keep_restore = SnapshotRestore.objects.all().order_by('-created_at')[:keep_restore_qty].values_list("id",
                                                                                                            flat=True)
        SnapshotRestore.objects.exclude(pk__in=list(keep_restore)).delete()
        logger.info("SnapshotRestore count after deletion: {}".format(SnapshotRestore.objects.all().count()))
        logger.info("finish snapshot_restore_finish_task")
    except Exception as e:
        logger.info("error snapshot_restore_finish_task: {}".format(e))
        pass


@task()
def create_active_wallet_task(active_wallet_id):
    msg = "Starting create_active_wallet_task id={}, waiting 5 seconds...".format(active_wallet_id)
    logger.info(msg)

    time.sleep(5)
    logger.info("Now yes, starting create_active_wallet_task id={}".format(active_wallet_id))

    try:
        active_wallet = ActiveWallet.objects.get(id=active_wallet_id)
        active_wallet.status = "processing"
        active_wallet.save()

        wenance_db_name = settings.MYSQL_WENANCE_DEV if getattr(settings, "MYSQL_WENANCE_DEV",
                                                                False) else active_wallet.snapshot_restore.database_name
        logger.info("using MYSQL_DB_NAME={}".format(wenance_db_name))

        wenance_engine = create_engine("mysql://{}:{}@{}/{}".format(
            settings.MYSQL_USER,
            settings.MYSQL_PASSWORD,
            settings.MYSQL_HOST,
            wenance_db_name
        ))

        core_barrido_engine = create_engine("mysql://{}:{}@{}/{}".format(
            settings.MYSQL_USER,
            settings.MYSQL_PASSWORD,
            settings.MYSQL_HOST,
            settings.CORE_BARRIDO_DB_NAME,
        ))

        mifos_engine = create_engine("mysql://{}:{}@{}/{}".format(
            settings.MIFOS_MYSQL_USER,
            settings.MIFOS_MYSQL_PASSWORD,
            settings.MIFOS_MYSQL_HOST,
            settings.MIFOS_DB_NAME
        ))

        if not database_exists(core_barrido_engine.url):
            msg = f"Creating {core_barrido_engine.url} database ..."
            logger.info(msg)
            create_database(core_barrido_engine.url)
            logger.info(f"{msg} Done!")



        # Create Active wallets
        create_active_wallet(wenance_engine)

        # Process salary file
        process_salary_file(wenance_db_name, core_barrido_engine, active_wallet)

        # Process cross selling active wallet data
        process_cross_selling(wenance_db_name, core_barrido_engine)

        # Process focus group
        process_focus_group(wenance_db_name, core_barrido_engine, active_wallet)

        # Update initial active wallet
        create_active_wallet_initial_data_manager(core_barrido_engine, wenance_engine, wenance_db_name)

        # Create the csv active wallet file for Debito Directo
        create_csv_active_wallet_file("create-cartera-activa-csv.sql", "debito_directo", ["AyN"],
                                      wenance_engine, active_wallet.result)

        # Create the csv active wallet file for Cobranzas Atencion al Cliente
        create_csv_active_wallet_file("create-cartera-activa-cobranzas-csv.sql", "cobranza_atencion_cliente", ["AyN"],
                                      wenance_engine, active_wallet.resultCollection)

        # Create the csv active wallet file for Renos
        create_csv_active_wallet_file("create-cartera-reno-csv.sql", "reno", ["input_firstname", "input_lastname"],
                                      wenance_engine, active_wallet.resultReno)

        # Create the csv active wallet file for cuotas cobradas
        try:
            create_csv_cuotas_cobradas_file('create-cartera-cuotas-cobradas-csv.sql', 'cuotas_cobradas', ["AyN"],
                                            wenance_engine, active_wallet.resultFeesCharged)
        except Exception as exc:
            logger.exception('Exception: ' + str(exc) + ' in cartera activa cuotas cobradas')

        # Create the csv active wallet file for mifos
        logger.info('Ingreso al metodo mifos')
        try:
            if "wenance" == getattr(settings, "APP_COMPANY"):
                create_csv_active_wallet_mifos_file('cartera-activa-cs-mifos.sql', 'mifos_ca', [],
                                                    mifos_engine,
                                                    active_wallet.resultMifosCa)
        except Exception as exc:
            logger.exception('Exception: ' + str(exc) + ' in cartera activa mifos')
        logger.info('Salgo del metodo mifos')

        logger.info(f"{msg} Done!")
        active_wallet.status = "finished"
        active_wallet.status_description = "Carteras generadas satisfactoriamente!"

        active_wallet.save()

    except Exception as error:
        msg = f"{msg} Fail!: {error}"
        logger.error(msg)
        active_wallet.status = "error"
        active_wallet.status_description = msg
        active_wallet.save()
        raise Exception(msg)

    msg = "Sending notification ... "
    logger.info(msg)
    NotificationClient().send_generic("Ya estan disponibles las Carteras!")
    logger.info(f"{msg} Done!")


def create_active_wallet(db_engine):
    execute_sql_sentence("DROP TABLE IF EXISTS cartera_activa_f_ultimo_debito", db_engine)
    execute_sql_sentence("DROP TABLE IF EXISTS cartera_activa", db_engine)
    execute_sql_script("create-cartera-activa.sql", db_engine)

    execute_sql_sentence("DROP TABLE IF EXISTS cartera_reno", db_engine)
    execute_sql_script("create-cartera-reno.sql", db_engine)
    execute_sql_script("update-cartera-reno.sql", db_engine)


def process_salary_file(db_name, db_engine, active_wallet):
    # Drop the temporary table client_salary if exists
    execute_sql_sentence("DROP TABLE IF EXISTS client_salary", db_engine)

    fn_s = active_wallet.salary.salary_csv.path
    msg = f"Processing salary csv file {fn_s} ..."
    logger.info(msg)
    try:
        # Fill the temporary table client_salary with the data in the csv file
        salary_csv = pandas.read_csv(active_wallet.salary.salary_csv.path, delimiter=";", quotechar='"',
                                     index_col=0, decimal=",")
        salary_csv.to_sql("client_salary", if_exists='replace', con=db_engine)
        logger.info(db_engine.execute("describe client_salary").fetchall())
        logger.info(f"{msg} Done!")

        # Update the table cartera_activa with the salaries
        msg = "Updating the table cartera_activa with the salaries ..."
        logger.info(msg)
        update_sql = text(
            "UPDATE `{}`.cartera_activa ca JOIN `{}`.client_salary s ON s.dni = ca.dni SET ca.sueldo = s.sueldos;".format(
                db_name, settings.CORE_BARRIDO_DB_NAME))
        db_engine.execute(update_sql)
        logger.info(f"{msg} Done!")

    except Exception as error:
        msg = f"{msg} Fail!: {error}"
        raise Exception(msg)


def create_csv_active_wallet_file(sql_select_csv_fn, output_csv_fn, columns_name_to_filter, db_engine,
                                  active_wallet_result, cartera_activa_table_name="cartera_activa"):
    msg = f"Reading {sql_select_csv_fn} ..."
    try:
        logger.info(msg)
        sql_file_csv = open(os.path.join(settings.MYSQL_SQL_DIR, sql_select_csv_fn))
        logger.info(f"{msg} Done!")

        msg = f"Executing pandas.read_sql for {sql_select_csv_fn} ..."
        logger.info(msg)
        result = pandas.read_sql(sql=text(sql_file_csv.read().strip().format(cartera_activa_table_name)), con=db_engine)
        logger.info(f"{msg} Done!")

        pattern = re.compile('[^a-zA-Z0-9\-._: \.\(\)\/]')
        msg = f"Removing characters '{pattern}' by '_' for {sql_select_csv_fn} data ..."
        logger.info(msg)
        for columns_name in columns_name_to_filter:
            result[columns_name] = result[columns_name].str.replace(pattern, '_')
        logger.info(f"{msg} Done!")
        fn = f'{output_csv_fn}_{datetime.datetime.now().strftime("%m-%d-%y-%H%M%S")}.zip'
        msg = f"Writing csv file {fn}... "
        logger.info(msg)
        result_csv = result.to_csv(header=False, decimal=',', index=False, encoding='utf-8-sig')
        zipbuff = io.BytesIO()
        with zipfile.ZipFile(zipbuff, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr(f"results_{output_csv_fn}.csv", result_csv.encode('utf-8-sig'))
        result = None
        result_csv = None
        gc.collect()
        active_wallet_result.save(fn, ContentFile(zipbuff.getvalue()))
        logger.info(f"{msg} Done!")
    except Exception as error:
        msg = f"{msg} Fail!: {error}"
        raise Exception(msg)


def create_csv_cuotas_cobradas_file(sql_select_csv_fn, output_csv_fn, columns_name_to_filter, db_engine,
                                  active_wallet_result, cartera_activa_table_name="cartera_activa"):
    msg = f"Reading {sql_select_csv_fn} ..."
    try:
        logger.info(msg)
        sql_file_csv = open(os.path.join(settings.MYSQL_SQL_DIR, sql_select_csv_fn))

        logger.info(f"{msg} Done!")
        d = date.today()
        offset = BMonthEnd()
        date2 = str(offset.rollforward(d) - BDay(2))[:-9]
        date1 = str(offset.rollback(d) - BDay(1))[:-9]

        data = sql_file_csv.read().replace('$1', date1).replace('$2', date2)

        msg = f"Executing pandas.read_sql for {sql_select_csv_fn} ..."
        logger.info(msg)
        result = pandas.read_sql(sql=text(data.format(cartera_activa_table_name)), con=db_engine)
        logger.info(f"{msg} Done!")

        pattern = re.compile('[^a-zA-Z0-9\-._: \.\(\)\/]')
        msg = f"Removing characters '{pattern}' by '_' for {sql_select_csv_fn} data ..."
        logger.info(msg)
        for columns_name in columns_name_to_filter:
            result[columns_name] = result[columns_name].str.replace(pattern, '_')
        logger.info(f"{msg} Done!")
        fn = f'{output_csv_fn}_{datetime.datetime.now().strftime("%m-%d-%y-%H%M%S")}.zip'
        msg = f"Writing csv file {fn}... "
        logger.info(msg)
        result_csv = result.to_csv(header=False, decimal=',', index=False, encoding='utf-8-sig')
        zipbuff = io.BytesIO()
        with zipfile.ZipFile(zipbuff, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr(f"results_{output_csv_fn}.csv", result_csv.encode('utf-8-sig'))
        result = None
        result_csv = None
        gc.collect()
        active_wallet_result.save(fn, ContentFile(zipbuff.getvalue()))
        logger.info(f"{msg} Done!")
    except Exception as error:
        msg = f"{msg} Fail!: {error}"
        raise Exception(msg)


def create_csv_active_wallet_mifos_file(sql_select_csv_fn, output_csv_fn, columns_name_to_filter, db_engine,
                                  active_wallet_result, cartera_activa_table_name="cartera_activa"):
    msg = f"Reading {sql_select_csv_fn} ..."
    try:
        logger.info(msg)
        sql_file_csv = open(os.path.join(settings.MYSQL_SQL_DIR, sql_select_csv_fn))
        logger.info(f"{msg} Done! Paso 1")

        msg = f"Executing pandas.read_sql for {sql_select_csv_fn} ..."
        logger.info(msg)
        sql_var = sql_file_csv.read().strip().format(cartera_activa_table_name)
        result = pandas.read_sql(sql=text(sql_var), con=db_engine)
        logger.info(f"{msg} Done! Paso 2")

        pattern = re.compile('[^a-zA-Z0-9\-._: \.\(\)\/]')
        msg = f"Removing characters '{pattern}' by '_' for {sql_select_csv_fn} data ..."
        logger.info(msg)
        for columns_name in columns_name_to_filter:
            result[columns_name] = result[columns_name].str.replace(pattern, '_')
        logger.info(f"{msg} Done! Paso 3")
        fn = f'{output_csv_fn}_{datetime.datetime.now().strftime("%m-%d-%y-%H%M%S")}.zip'
        msg = f"Writing csv file {fn}... "
        logger.info(msg)
        result_csv = result.to_csv(header=False, decimal=',', index=False, encoding='utf-8-sig')
        zipbuff = io.BytesIO()
        with zipfile.ZipFile(zipbuff, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr(f"results_{output_csv_fn}.csv", result_csv.encode('utf-8-sig'))
        result = None
        result_csv = None
        gc.collect()
        active_wallet_result.save(fn, ContentFile(zipbuff.getvalue()))
        logger.info(f"{msg} Done! Paso 4")
    except Exception as error:
        logger.error(error)
        msg = f"{msg}  - Exception mifos file Fail!: {error}"
        raise Exception(msg)


def process_focus_group(wenance_db_name, db_engine, active_wallet):
    # Drop the temporary table client_focus_group if exists
    execute_sql_sentence("DROP TABLE IF EXISTS client_focus_group", db_engine)

    try:
        if active_wallet.focusgroup:
            msg = f"Processing focus group csv file {active_wallet.focusgroup.focusgroup_csv.path} ..."
            logger.info(msg)
            focusgroup_csv = pandas.read_csv(active_wallet.focusgroup.focusgroup_csv.path, delimiter=",",
                                             quotechar='"', index_col=0, decimal=",")
            focusgroup_csv.to_sql("client_focus_group", if_exists='replace', con=db_engine)
            logger.info(db_engine.execute("describe client_focus_group").fetchall())
            logger.info(f"{msg} Done!")

            msg = "Updating client focus group ..."
            logger.info(msg)
            update_sql = text(
                "UPDATE `{}`.cartera_activa ca JOIN {}.client_focus_group f "
                "ON f.dni = ca.dni SET ca.Grupo = f.grupo;".format(
                    wenance_db_name, settings.CORE_BARRIDO_DB_NAME)
            )
            db_engine.execute(update_sql)
            logger.info(f"{msg} Done!")
        else:
            logger.info("Active wallet without focus group!")

    except Exception as error:
        msg = f"{msg} Fail!: {error}"
        raise Exception(msg)


def process_cross_selling(db_name, db_engine, ca_table_name = "cartera_activa"):
    execute_sql_sentence("DROP TABLE IF EXISTS cross_selling_active_wallet", db_engine)

    if getattr(settings, "MIFOS_URL", False):
        try:
            msg = "Getting cross selling active wallet data from FINERACT ... "
            logger.info(msg)
            mifos_wallet = MifosClient().export_active_wallet()
            logger.info(f"{msg} Done!")

            if mifos_wallet.status_code == 200:
                msg = "Cross selling active wallet return status 200! Processing ..."
                logger.info(msg)
                mifos_wallet_csv = pandas.read_csv(io.BytesIO(mifos_wallet.content), delimiter=",", quotechar='"',
                                                   decimal=".")
                mifos_wallet_csv.to_sql("cross_selling_active_wallet", if_exists='replace', con=db_engine)
                logger.info(f"{msg} Done!")

                msg = "Indexing cross selling table..."
                logger.info(msg)
                execute_sql_sentence("CREATE INDEX cross_selling_active_wallet__external_id ON cross_selling_active_wallet (externalId)", db_engine)

                msg = "Updating cartera_activa with cross selling active wallet data..."
                logger.info(msg)
                update_sql = text(
                    "UPDATE `{}`.{} ca JOIN {}.cross_selling_active_wallet s "
                    "ON s.externalId = ca.Id_Cliente SET ca.Deuda_crossselling = s.totalDue;".format(
                        db_name, ca_table_name, settings.CORE_BARRIDO_DB_NAME)
                )
                db_engine.execute(update_sql)

                logger.info(f"{msg} Done!")

            else:
                logger.info("Error calling cross selling active wallet: {} | {}".format(mifos_wallet.status_code,
                                                                                        mifos_wallet.reason))

        except Exception as error:
            msg = f"{msg} Fail!: {error}"
            raise Exception(msg)

    else:
        logger.info("Cross selling active wallet process inactive!")


def execute_sql_script(sql_script_fn, db_engine, cartera_activa_table_name='cartera_activa'):
    msg = f"Processing SQL file script '{sql_script_fn}'"\
            f"with params '{settings.CORE_BARRIDO_DB_NAME}' as 'core barrido' schema,  '{settings.MYSQL_NAME}'"\
            f"as Mambu schema, and '{cartera_activa_table_name}' as 'cartera activa' table ..."
    try:
        logger.info(msg)
        sql_file = open(os.path.join(settings.MYSQL_SQL_DIR, sql_script_fn))
        sql_script = text(sql_file.read().strip().format(settings.CORE_BARRIDO_DB_NAME, settings.MYSQL_NAME,
                                                              cartera_activa_table_name))
        db_engine.execute(sql_script)
        logger.info(f"{msg} Done!")

    except Exception  as error:
        msg = f"{msg} Fail!: {error}"
        raise Exception(msg)


def execute_sql_sentence(sql_sentence, db_engine):
    msg = f"Executing '{sql_sentence}' ..."
    try:
        logger.info(msg)
        db_engine.execute(sql_sentence)
        logger.info(f"{msg} Done!")
    except Exception as error:
        msg = f"{msg} Fail!: {error}"
        raise Exception(msg)


def create_active_wallet_initial_data_manager(core_barrido_engine, wenance_engine, db_name):
    try:
        collection = CollectionCycle.objects.filter(start_process_date=datetime.date.today()).first()
        if collection:
            execute_sql_sentence("DROP TABLE IF EXISTS cartera_activa_inicial", core_barrido_engine)

            execute_sql_sentence(
                "CREATE TABLE cartera_activa_inicial SELECT * FROM `{}`.cartera_activa".format(db_name),
                core_barrido_engine)

            execute_sql_sentence("CREATE INDEX cartera_activa_init_ID_IDX USING BTREE ON cartera_activa_inicial (Id)",
                                 core_barrido_engine)

        else:
            check = core_barrido_engine.execute("SHOW TABLES LIKE 'cartera_activa_inicial'").fetchall()
            if len(check) < 1:
                execute_sql_sentence(
                    "CREATE TABLE cartera_activa_inicial SELECT * FROM `{}`.cartera_activa".format(db_name),
                    core_barrido_engine)
                execute_sql_sentence(
                    "CREATE INDEX cartera_activa_init_ID_IDX USING BTREE ON cartera_activa_inicial (Id)",
                    core_barrido_engine)

        execute_sql_script("update-cartera-activa.sql", wenance_engine)

        if collection:
            fn = "create-cartera-activa-inicial-csv.sql"
            msg = f"Reading SQL file script {fn} ..."
            logger.info(msg)
            sql_file_csv = open(os.path.join(settings.MYSQL_SQL_DIR, fn))
            result = pandas.read_sql(sql=text(sql_file_csv.read().strip()), con=core_barrido_engine)
            logger.info(f"{msg} Done!")

            pattern = '[^a-zA-Z0-9\-._: \.\(\)\/]'
            msg = f"Replacing '{pattern}' by '_' for {fn} data ..."
            logger.info(msg)

            result['AyN'] = result['AyN'].str.replace(pattern, '_')
            logger.info(f"{msg} Done!")

            fn = "{}.zip".format(datetime.datetime.now().strftime("%m-%d-%y-%H%M%S"))
            msg = f"Generating results for initial active wallet in {fn} ..."
            logger.info(msg)
            result_csv = result.to_csv(header=False, decimal=',', index=False, encoding='utf-8-sig')
            zipbuff = io.BytesIO()
            with zipfile.ZipFile(zipbuff, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr("results-cartera-activa-inicial.csv", result_csv.encode('utf-8-sig'))
            collection.result.save(fn, ContentFile(zipbuff.getvalue()))
            collection.save()
            logger.info(f"{msg} Done!")

    except Exception as error:
        msg = f"{msg} Fail!: {error}"
        raise Exception(msg)


@task()
def drop_database_task(database_name):
    logger.info("drop database {}".format(database_name))
    drop_database("mysql://{}:{}@{}/{}".format(
        settings.MYSQL_USER,
        settings.MYSQL_PASSWORD,
        settings.MYSQL_HOST,
        database_name
    ))


@task()
def active_wallet_start_task(active_wallet_process_id):
    logger.info("waiting to start active_wallet_start_task id={}".format(active_wallet_process_id))
    time.sleep(5)
    logger.info("now yes, starting active_wallet_start_task id={}".format(active_wallet_process_id))

    active_wallet_process = ActiveWalletProcess.objects.get(id=active_wallet_process_id)
    snapshot_signal_kwargs = {
        'signal': signals.post_save,
        'receiver': core_signals.snapshot_handler,
        'sender': Snapshot,
    }
    with TempSignalDisconnect(**snapshot_signal_kwargs):
        snapshot = Snapshot.objects.create(
            user=active_wallet_process.user,
        )
        callback = "{}{}".format(
            getattr(settings, "APP_BASE_URL"),
            reverse("active_wallet_process_callback", args=(active_wallet_process.id, snapshot.id))
        )
        generate_snapshot_task(snapshot.id, callback)
    snapshot = Snapshot.objects.get(id=snapshot.id)
    if snapshot.status == "cancelled":
        active_wallet_process.change_status("failure")
    else:
        active_wallet_process.change_status("mambu_generating")


@task()
def active_wallet_finish_task():
    logger.info("starting active_wallet_finish_task")

    try:
        keep_qty = getattr(settings, "SNAPSHOTS_TO_KEEP", 10)
        keep_restore_qty = getattr(settings, "SNAPSHOTS_RESTORE_TO_KEEP", 4)
        logger.info("snapshots to keep: {}".format(keep_qty))
        logger.info("snapshots_restore to keep: {}".format(keep_restore_qty))

        logger.info("deleting Snapshot")
        logger.info("Snapshot count before deletion: {}".format(Snapshot.objects.all().count()))
        keep = Snapshot.objects.all().order_by('-created_at')[:keep_qty].values_list("id", flat=True)
        Snapshot.objects.exclude(pk__in=list(keep)).delete()
        logger.info("Snapshot count after deletion: {}".format(Snapshot.objects.all().count()))

        logger.info("deleting SnapshotRestore")
        logger.info("SnapshotRestore count before deletion: {}".format(SnapshotRestore.objects.all().count()))
        keep_restore = SnapshotRestore.objects.all().order_by('-created_at')[:keep_restore_qty].values_list("id",
                                                                                                            flat=True)
        SnapshotRestore.objects.exclude(pk__in=list(keep_restore)).delete()
        logger.info("SnapshotRestore count after deletion: {}".format(SnapshotRestore.objects.all().count()))
        logger.info("finish active_wallet_finish_task")
    except Exception as e:
        logger.info("error active_wallet_finish_task: {}".format(e))
        pass


@task()
def generic_cashin_init_task(generic_cashin_id):
    logger.info("waiting to start generic_cashin_init_task id={}".format(generic_cashin_id))
    time.sleep(5)
    logger.info("now yes, starting generic_cashin_init_task id={}".format(generic_cashin_id))

    generic_cashin = GenericCashin.objects.get(id=generic_cashin_id)
    cg_csv = pandas.read_csv(generic_cashin.cashin_csv.path, delimiter=",", quotechar='"', index_col=False, header=0,
                             decimal=".", usecols=["Estado", "Importe", "Banco"])
    generic_cashin.bank = cg_csv.head(1).Banco[0]
    resumen = "Resumen transacciones banco '{}':".format(generic_cashin.bank)
    data = cg_csv.groupby(['Estado']).Importe.sum()
    for stat, amount in data.iteritems():
        resumen = resumen + " " + (stat + "=" + str(amount))

    generic_cashin.resume = resumen

    '''
    name = generic_cashin.cashin_csv.name.replace('results/', '')
    file = generic_cashin.cashin_csv.read()

    zipbuff = io.BytesIO()
    with zipfile.ZipFile(zipbuff, "a", zipfile.ZIP_DEFLATED, False) as zip_file:ter
        zip_file.writestr(name, file)

    generic_cashin.cashin_csv.save("{}-{}.zip".format(name, datetime.datetime.now().strftime("%m-%d-%y-%H%M%S")),
                               ContentFile(zipbuff.getvalue()))    
    '''

    generic_cashin.change_status("pending_approve")


@task()
def generic_cashin_approve_task(generic_cashin_id):
    generic_cashin = GenericCashin.objects.get(id=generic_cashin_id)
    core_middleware_client = CoreMiddlewareClient()

    file = generic_cashin.cashin_csv.read()
    filename = generic_cashin.cashin_csv.name.replace('results/', '')

    zipbuff = io.BytesIO()
    with gzip.open(zipbuff, 'wb') as f:
        f.write(file)

    response = core_middleware_client.cashin_generic_process("generico",
                                                             consumer_username=generic_cashin.consumer_username,
                                                             file_contents=zipbuff.getvalue(),
                                                             file_name=filename)
    if response.status_code == 202:
        generic_cashin.change_status("finished")
    else:
        generic_cashin.error_detail = response.content
        generic_cashin.change_status("error")


@task()
def validate_and_auto_process_task():
    logger.info("starting validate_and_auto_process_task")
    snapshot_retore = SnapshotRestore.objects.filter(created_at__date=datetime.date.today()).first()
    if snapshot_retore:
        logger.info("validate_and_auto_process_task: restore already created")
    else:
        logger.info("validate_and_auto_process_task: restore not yet created")
        user = User.objects.filter(username="admin").first()
        if user:
            active_wallet_process = ActiveWalletProcess.objects.create(user=user)
            logger.info("validate_and_auto_process_task: active_wallet_process created, id={}".format(
                active_wallet_process.id))
        else:
            logger.error("validate_and_auto_process_task: user 'admin' not exists")


@task()
def run_auto_process_task():
    logger.info("starting run_auto_process_task")
    aw_process = ActiveWalletProcess.objects.filter(created_at__date=datetime.date.today(),
                                                    status__in=["pending", "mambu_generating", "downloading",
                                                                "restoring", "wallet_generating"]).first()
    if aw_process:
        logger.info("run_auto_process_task: process already created")
    else:
        logger.info("run_auto_process_task: process not yet created")
        user = User.objects.filter(username="admin").first()
        if user:
            active_wallet_process = ActiveWalletProcess.objects.create(user=user)
            logger.info("run_auto_process_task: active_wallet_process created, id={}".format(active_wallet_process.id))
        else:
            logger.error("run_auto_process_task: user 'admin' not exists")


class ActiveWalletCompleteProcess(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Error handler.

        This is run by the worker when the task fails.

        Arguments:
            exc (Exception): The exception raised by the task.
            task_id (str): Unique id of the failed task.
            args (Tuple): Original arguments for the task that failed.
            kwargs (Dict): Original keyword arguments for the task that failed.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.
        Returns:
            None: The return value of this handler is ignored.
        """
        logger.info("error ActiveWalletCompleteProcess, task_id={}", task_id)
        logger.exception(exc)

        active_wallet_process = ActiveWalletProcess.objects.get(id=args[0])
        active_wallet_process.change_status("failure", failure_reason="Step: {}\nReason: {}".format(
            active_wallet_process.get_status_display(),
            exc.__str__()
        ))

    def run(self, active_wallet_process_id, snapshot_id, *args, **kwargs):
        active_wallet_process = ActiveWalletProcess.objects.get(id=active_wallet_process_id)
        user = active_wallet_process.user
        salary = Salary.objects.last()
        focusgroup = FocusGroup.objects.last()
        snapshot = Snapshot.objects.get(id=snapshot_id)
        active_wallet_process.change_status("downloading")
        download_snapshot_task(snapshot.id)
        snapshot_restore_signal_kwargs = {
            'signal': signals.post_save,
            'receiver': core_signals.snapshot_restore_handler,
            'sender': SnapshotRestore,
        }
        with TempSignalDisconnect(**snapshot_restore_signal_kwargs):
            snapshot_restore = SnapshotRestore.objects.create(
                user=user,
                snapshot=snapshot
            )
            active_wallet_process.change_status("restoring")
            restore_snapshot_task(snapshot_restore.id)
        active_wallet_signal_kwargs = {
            'signal': signals.post_save,
            'receiver': core_signals.active_wallet_handler,
            'sender': ActiveWallet,
        }
        with TempSignalDisconnect(**active_wallet_signal_kwargs):
            active_wallet = ActiveWallet.objects.create(
                user=user,
                snapshot_restore=snapshot_restore,
                salary=salary,
                focusgroup=focusgroup
            )
            active_wallet_process.change_status("wallet_generating")
            create_active_wallet_task(active_wallet.id)
        active_wallet_process.active_wallet = active_wallet
        active_wallet_process.status = "finished"
        active_wallet_process.save()


class CleanUp(PeriodicTask):
    run_every = datetime.timedelta(hours=8)

    def run(self, *args, **kwargs):
        logger.info("starting CleanUp")
        inspect = self.app.control.inspect()
        for node, tasks in inspect.active().items():
            for current_task in tasks:
                if self.name == current_task.get("name") and not self.request.id == current_task.get("id"):
                    logger.info("{} is running by worker {}".format(self.name, node))
                    return
        logger.info("cleaning")
        barrido_ui_engine = create_engine("mysql://{}:{}@{}".format(
            settings.MYSQL_USER,
            settings.MYSQL_PASSWORD,
            settings.MYSQL_HOST,
        ))
        databases = [db for (db,) in barrido_ui_engine.execute("show databases") if re.findall(r"([a-fA-F\d]{32})", db)]
        for db in databases:
            queryset = SnapshotRestore.objects.filter(database_name=db)
            if not queryset.exists():
                logger.warning(
                    "deleting snapshot restores with ID's {}".format(
                        ",".join([str(id) for id in queryset.values_list("id", flat=True)])
                    )
                )
                queryset.delete()
        snapshots_orphans = Snapshot.objects.filter(snapshotrestore__isnull=True)
        logger.warning(
            "deleting snapshots with ID's {}".format(
                ",".join([str(id) for id in snapshots_orphans.values_list("id", flat=True)])
            )
        )
        snapshots_orphans.delete()


@task()
def active_wallet_report_task(active_wallet_report_id):
    logger.info("stating active_wallet_report_task id={}".format(active_wallet_report_id))
    report = ActiveWalletReport.objects.get(id=active_wallet_report_id)
    report.status = "generating"
    report.save()

    token = getattr(settings, "BONDI_XPUBTOKEN_CA_REPORT")
    topic = getattr(settings, "BONDI_TOPIC_CA_REPORT")
    message = {"active_wallet_report_id": active_wallet_report_id}

    logger.info("active_wallet_report_task id={} sending message, token={}, topic={}, message={}".
                format(active_wallet_report_id, token, topic, message))
    response = BondiClient().pub_message(token, topic, message)
    if response:
        logger.info("active_wallet_report_task id={} sent successfully".format(active_wallet_report_id))
    else:
        logger.info("active_wallet_report_task id={} sent with error {}:{}".format(
            active_wallet_report_id, response.status_code, response.reason))


@task()
def completar_reno(active_wallet_id):
    wa = ActiveWallet.objects.get(id=active_wallet_id)
    cas = CarteraActivaService(wa)


@task()
def delete_active_wallet_report(active_wallet_report_id):
    logger.info("deleting active_wallet_report_manual_task id={}".format(active_wallet_report_id))
    core_barrido_engine = create_engine("mysql://{}:{}@{}/{}".format(
        settings.MYSQL_USER,
        settings.MYSQL_PASSWORD,
        settings.MYSQL_HOST,
        settings.CORE_BARRIDO_DB_NAME,
    ))
    logger.info("DROP TABLE IF EXISTS cartera_activa_{}".format(active_wallet_report_id))
    core_barrido_engine.execute("DROP TABLE IF EXISTS cartera_activa_{}".format(active_wallet_report_id))


class ActiveWalletReportManual(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        report = ActiveWalletReport.objects.get(id=args[0])
        report.status = "error"
        report.status_description = exc
        logger.exception(exc)
        report.save()

    def run(self, active_wallet_report_id):
        logger.info("waiting to start active_wallet_report_manual_task id={}".format(active_wallet_report_id))
        time.sleep(5)
        logger.info("now yes, starting active_wallet_report_manual_task id={}".format(active_wallet_report_id))
        report = ActiveWalletReport.objects.get(id=active_wallet_report_id)
        report.status = "generating"
        report.save()
        cas = CarteraActivaService(report)
        cas.prepare()
        cas.jasper_to_sql(report.origin_report, {'Id': VARCHAR(32)})
        report.status = "processing"
        report.save()
        process_info_csv(cas, report.salary, 'salary')
        process_info_csv(cas, report.focusgroup, 'focusgroup')
        # Process cross selling active wallet data

        # TODO: Encapsular (pasarle el cas)
        wenance_engine = create_engine("mysql://{}:{}@{}/{}".format(
            settings.MYSQL_USER,
            settings.MYSQL_PASSWORD,
            settings.MYSQL_HOST,
            cas.database_name
        ))
        # TODO: Encapsular
        process_cross_selling(cas.database_name, wenance_engine, f"cartera_activa_{report.id}")

        # Create the csv active wallet file for Debito Directo
        errors = 0
        max_errors = 2
        try:
            create_csv_active_wallet_file("create-cartera-activa-csv.sql", "debito_directo", ["AyN"],
                                          cas.barrido_engine, report.result,
                                          cartera_activa_table_name=f"cartera_activa_{report.id}")
        except Exception as exc:
            errors = errors + 1
            logger.error("Unable to generate create-cartera-activa-csv (see error bellow)")
            logger.exception(exc)

        # Create the csv active wallet file for Cobranzas Atencion al Cliente
        try:
            create_csv_active_wallet_file("create-cartera-activa-cobranzas-csv.sql", "cobranza_atencion_cliente", ["AyN"],
                                          cas.barrido_engine, report.resultCollection,
                                          cartera_activa_table_name=f"cartera_activa_{report.id}")
        except Exception as exc:
            errors = errors + 1
            logger.error("Unable to generate create-cartera-activa-cobranzas-csv (see error bellow)")
            logger.exception(exc)

        # Create the csv active wallet file for Renos
        # create_csv_active_wallet_file("create-cartera-reno-csv.sql", "reno", ["input_firstname", "input_lastname"],
        #                              cas.barrido_engine, report.result,
        #                              cartera_activa_table_name=f"cartera_activa_{report.id}")

        if errors >= max_errors:
            raise Exception("No CSV report could be generated.")

        report.status = "finished"
        report.save()
        logger.info("finishing active_wallet_report_manual_task")


@task()
def active_wallet_report_callback_task(active_wallet_report_id, report_url):
    logger.info("Starting active_wallet_report_callback_task")
    time.sleep(5)
    report = ActiveWalletReport.objects.get(id=active_wallet_report_id)
    report.status = "generating"
    cas = CarteraActivaService(report)
    cas.jasper_to_sql(report_url, {'Id': VARCHAR(32)})
    report.status = "processing"
    cas.info_csv_to_ca(report.salary.salary_csv, 'salary')
    # cas.csv_to_sql(report.resultReno.file, 'reno')
    report.status = "finished"
    report.save()
    logger.info("finishing active_wallet_report_callback_task")
    # Todo, 1 Almacenar archivo zip
    # Todo, 2 Descomprimir csvs
    # Todo, 3 Crear tabla


def process_info_csv(cartera_activa_service, info_model, info_name):
    if info_model is None:
        return
    logger.info("executing process_info_csv from '{}'".format(info_name))
    csv_element = getattr(info_model, f"{info_name}_csv")
    cartera_activa_service.info_csv_to_sql(csv_element, info_name)
    cartera_activa_service.info_sql_to_ca(info_name)
    logger.info("finished process_info_csv from '{}'".format(info_name))
