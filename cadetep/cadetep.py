import requests
from requests.models import Response
from requests.exceptions import ConnectionError
from django.conf import settings


class CadetePClient(object):
    def __init__(self):
        self.cadetep_url = getattr(settings, "CADETEP_URL")

    def make_request(self, method, endpoint, files=None, data=None, json=None):
        headers = {
            "Content-Type": "application/json"
        }
        url = "{}{}".format(self.cadetep_url, endpoint)
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

    def manual_input(self, file, agreement, user):
        return self.make_request(
            "post", "/manual-input",
            files={
                "file": file
            },
            data={
                "agreement": agreement,
                "user": user.username
            }
        )

    def get_tenants(self):
        return self.make_request("get", "/tenant")

    def get_channels(self, tenant):
        return self.make_request("get", "/channel?tenant={}".format(tenant))

    def get_agreements(self, tenant, channel):
        return self.make_request("get", "/agreement?tenant={}&channel={}".format(tenant, channel))
