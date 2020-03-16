import os
import shutil
import datetime
import pandas
import re

from django.test import TestCase
from django.conf import settings
from unittest.mock import patch
from unittest import skip
from sqlalchemy import BIGINT, VARCHAR, create_engine, text

# from core.types.steroids_file.steroids_compressed_file.steroids_zip_file import SteroidsZipFile
from core.services.cartera_activa_service import CarteraActivaService


class BarridoDataBase:
    core_barrido_engine = create_engine("mysql://{}:{}@{}/{}".format(
        settings.MYSQL_USER,
        settings.MYSQL_PASSWORD,
        settings.MYSQL_HOST,
        settings.CORE_BARRIDO_DB_NAME,
    ))


class BaseTestClass:
    pass


class FilesToolCase(TestCase, BaseTestClass):
    SPEC_FOLDER = '.spec'
    TEST_SUBJECTS_FOLDER = "misc/test_subjects"

    def setUp(self):
        if os.path.isdir(self.SPEC_FOLDER):
            shutil.rmtree(self.SPEC_FOLDER)
        os.mkdir(self.SPEC_FOLDER)

    def tearDown(self):
        if os.path.isdir(self.SPEC_FOLDER):
            shutil.rmtree(self.SPEC_FOLDER)


class CarteraActivaBaseCase(TestCase):
    @patch('core.models.ActiveWalletReport', autospec=True)
    def setUp(self):
        with patch('core.models.ActiveWalletReport', autospec=True) as mock_awr:
            self.active_wallet_loco = mock_awr
            super().setUp()


class ActiveWalletSnapshotCase(FilesToolCase, BarridoDataBase):
    CA_CLEAN_STRING_SQL = "sql/cartera-activa-initial-clean-string-test.sql"

    # @patch('core.tasks', autospec=True)
    @skip('No implementado')
    def test_clean_dataframe_data(self):
        sql_file_csv = open(f"{self.TEST_SUBJECTS_FOLDER}/{self.CA_CLEAN_STRING_SQL}")
        result = pandas.read_sql(sql=text(sql_file_csv.read().strip()), con=self.core_barrido_engine)
        pattern = re.compile("[^a-zA-Z0-9\-._: \.\(\)\/]")
        result['AyN'] = result['AyN'].str.replace(pattern, '_')
        self.assertTrue("_" in f"{result.loc[11:11,'AyN']}")


class ActiveWalletServiceCase(FilesToolCase, BaseTestClass):
    URL_TEST = "http://www.fragua.com.ar/envia/Archivo.zip"
    JASPER_FILE = "jasper/jasper.zip"

    def prepare_active_wallet(self, active_wallet):
        active_wallet.id = f"{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        return active_wallet

    @patch('core.models.ActiveWalletReport', autospec=True)
    @skip('No implementado')
    def test_cartera_activa_csv_to_sql(self, mock_active_wallet):
        # Escuchar desde bondi para la descarga
        # Enriquecedor
        mock_active_wallet = self.prepare_active_wallet(mock_active_wallet)
        # download_file(self.URL_TEST, destination_file)
        cartera_activa_service = CarteraActivaService(mock_active_wallet)
        process_result = cartera_activa_service.jasper_to_sql(
            open(f"{self.TEST_SUBJECTS_FOLDER}/{self.JASPER_FILE}", 'rb'),
            {'Id': BIGINT, 'Dni': VARCHAR(20)})
        # Todo, ENRIQUECER CON CROSS SELLING
        # Todo, ENRIQUECER CON FOCUS GROUP
        # Todo, UPDATE INITIAL DATA MANAGER LOCO
        self.assertTrue(process_result)

    @patch('core.models.ActiveWalletReport', autospec=True)
    @skip('No implementado')
    def test_salary_to_cartera_activa_sql(self, awr):
        awr = self.prepare_active_wallet(awr)
        cartera_activa_service = CarteraActivaService(awr)
        cartera_activa_service.info_csv_to_sql(open("misc/test_subjects/salary/salary.csv", 'r'), "salary")
        cartera_activa_service.info_sql_to_ca("salary")

    @patch('core.models.ActiveWalletReport', autospec=True)
    @skip('No implementado')
    def test_xselling_to_cartera_activa_sql(self, awr):
        awr = self.prepare_active_wallet(awr)
        cartera_activa_service = CarteraActivaService(awr)
        cartera_activa_service.info_csv_to_sql(open("misc/test_subjects/salary/salary.csv", 'r'), "cross_selling")
