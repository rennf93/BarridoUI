import datetime
import io
import os
import re
import pandas
import zipfile
from django.core.files.base import ContentFile
from django.conf import settings
from core.models import CollectionCycle
from celery.utils.log import get_task_logger
from sqlalchemy import text

logger = get_task_logger(__name__)


def create_active_wallet_initial_data_manager(sql_service, cartera_activa):
    """
    Args:
        sql_service (SqlService):
        cartera_activa (ActiveWalletReport):
    Returns:
    """
    # barrido_ui_engine.url.database
    collection = CollectionCycle.objects.filter(start_process_date=datetime.date.today()).first()
    if collection:
        logger.info(f"generating freeze cartera-activa: {collection}")
        logger.info("drop table cartera_activa_inicial if exists")
        sql_service.execute_sql_query("DROP TABLE IF EXISTS cartera_activa_inicial;")
        logger.info("freezing cartera_activa_inicial")
        sql_service.execute_sql_query(
            f"CREATE TABLE cartera_activa_inicial SELECT * FROM `cartera_activa_{cartera_activa.id}`;"
        )
        sql_service.execute_sql_query(
            "CREATE INDEX cartera_activa_init_ID_IDX USING BTREE ON cartera_activa_inicial (Id);"
        )
        logger.info("freezing cartera_activa_inicial finished")
    else:
        logger.info("date out for freeze cartera-activa")
        connection = sql_service.database_engine.raw_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'cartera_activa_inicial'")
            check = list(cursor.fetchall())
            cursor.close()
            connection.commit()
        except Exception as e:
            print(e)
            raise e
        finally:
            connection.close()
        if len(check) < 1:
            logger.info("creating first cartera_activa_inicial")
            sql_service.execute_sql_query(
                f"CREATE TABLE cartera_activa_inicial SELECT * FROM cartera_activa_{cartera_activa.id}"
            )
            sql_service.execute_sql_query(
                "CREATE INDEX cartera_activa_init_ID_IDX USING BTREE ON cartera_activa_inicial (Id)"
            )


def save_cartera_activa_inicial_report(core_barrido_engine):
    collection = CollectionCycle.objects.filter(start_process_date=datetime.date.today()).first()
    if collection:
        logger.info("saving cartera_activa_inicial...")
        sql_file_csv = open(os.path.join(settings.MYSQL_SQL_DIR, "create-cartera-activa-inicial-csv.sql"))
        logger.info("reading create-cartera-activa-inicial-csv.sql for cartera_activa_inicial ...")
        result = pandas.read_sql(sql=text(sql_file_csv.read().strip()), con=core_barrido_engine)
        for index, row in result.iterrows():
            row['AyN'] = re.sub('[^a-zA-Z0-9\-._: \.\(\)\/]', '_', row['AyN'])
        logger.info("generating results cartera_activa_inicial...")
        result_csv = result.to_csv(header=False, decimal=',', index=False, encoding='utf-8-sig')
        zipbuff = io.BytesIO()
        with zipfile.ZipFile(zipbuff, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr("results-cartera-activa-inicial.csv", result_csv.encode('utf-8-sig'))
        fn = "{}.zip".format(datetime.datetime.now().strftime("%m-%d-%y-%H%M%S"))
        collection.result.save(fn, ContentFile(zipbuff.getvalue()))
        collection.save()
        logger.info(f"Results for cartera_activa_inicial was written in {fn}!")
