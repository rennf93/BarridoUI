import os.path
from celery.utils.log import get_task_logger
from sqlalchemy import text


logger = get_task_logger(__name__)


def log_and_execute_sentence(database_engine, sentence):
    logger.info(sentence)
    conn = database_engine.connect()
    conn.execute(sentence)
    conn.close()


def log_and_execute_file(database_engine, sql_file_stream, sql_tag_name=None):
    sql_tag_name = sql_tag_name if sql_tag_name is not None else os.path.basename(sql_file_stream.name)
    logger.info(f"Processing SQL file for {sql_tag_name}")
    conn = database_engine.connect()
    conn.execute(text(sql_file_stream.read().strip()))
    conn.close()
