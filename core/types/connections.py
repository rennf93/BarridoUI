from django.conf import settings


def mysql_engine(db_name=settings.CORE_BARRIDO_DB_NAME):
    return f"mysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}/{db_name}"


def mysql_barrido_ui_engine(db_name):
    return f"mysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}/{db_name}"
