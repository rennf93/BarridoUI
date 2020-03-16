import requests
from requests.models import Response
from requests.exceptions import ConnectionError
from django.conf import settings
from core.modules.filters import RequestFilter


class CadeteClient(object):
    def __init__(self, user):
        self.cadete_url = getattr(settings, "CADETE_URL")
        self.user = user

    def make_request(self, method, endpoint, files=None, data=None, json=None):
        headers = {
            "Content-Type": "application/json",
            "X_CADETE_CONFIG_TOKEN": "6D462DD0F0EF48CA6F9FA5173683BE17",
            "X_USER_ID": str(self.user.id)
        }
        url = "{}{}".format(self.cadete_url, endpoint)
        request_module = getattr(requests, method)
        try:
            if files:
                return request_module(url, files=files, data=data)
            return request_module(url, headers=headers, json=json)
        except ConnectionError:
            response = Response()
            response.status_code = 400
            response.json = lambda: {}
            return response

    def operations(self):
        return self.make_request("get", "/operations?size=100{}".format(RequestFilter.filtro_cadete(self.user, '&')))

    def filter_operations(self, filter_name, filter_value):
        return self.make_request("get", "/operations?size=100&{}={}".format(
            filter_name, filter_value, RequestFilter.filtro_cadete(self.user, '&')))

    def get_operation(self, operation_id):
        return self.make_request("get", "/operations/{}".format(operation_id))

    def download_operation_rendition_file(self, operation_id):
        return self.make_request("get", "/operations/{}/rendition_file".format(operation_id))

    def download_operation_warehouse_file(self, operation_id, file_id):
        return self.make_request("get", "/operations/{}/warehouse_file/{}".format(operation_id, file_id))

    def configurations(self, config_type):
        return self.make_request("get", "/{}?size=100{}".format(
            config_type,
            RequestFilter.filtro_cadete(self.user, '&'))
                                 )

    def get_configuration(self, config_type, configuration_id):
        return self.make_request("get", "/{}/{}".format(config_type, configuration_id))

    def update_configuration(self, configuration_id, update_data, config_type):
        return self.make_request("patch", "/{}/{}".format(config_type, configuration_id), json=update_data)

    def create_bank_configuration(self, create_data):
        return self.make_request("post", "/configurations", json=create_data)

    def download_operation_rendition_file_by_md5(self, operation_md5):
        return self.make_request("get", "/operations/md5/{}".format(operation_md5))
