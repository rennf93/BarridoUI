import requests
from requests.models import Response
from django.conf import settings


class MifosClient(object):
    def __init__(self):
        self.mifos_url = getattr(settings, "MIFOS_URL")
        self.mifos_api_auth = getattr(settings, "MIFOS_API_AUTHORIZATION")

    def make_request(self, method, endpoint, files=None, data=None, json=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic {}".format(self.mifos_api_auth),
        }
        url = "{}{}".format(self.mifos_url, endpoint)
        request_module = getattr(requests, method)
        try:
            if files:
                del headers["Content-Type"]
                return request_module(url, headers=headers, files=files, data=data)
            return request_module(url, headers=headers, json=json)
        except Exception:
            response = Response()
            response.status_code = 400
            response.json = lambda: {}
            return response

    def export_active_wallet(self):
        req = "/runreports/Cartera_Activa_CrossSelling?tenantIdentifier={}&exportCSV=true".format("default")
        return self.make_request("get", req)

