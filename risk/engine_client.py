import requests
from requests.models import Response
from requests.exceptions import ConnectionError
from django.conf import settings


class EngineClient(object):
    def __init__(self):
        self.engine_url = getattr(settings, "ENGINE_URL")
        self.engine_user = getattr(settings, "ENGINE_USER")
        self.engine_password = getattr(settings, "ENGINE_PASSWORD")

    def make_request(self, method, endpoint, json=None):
        headers = {
            "Content-Type": "application/json",
        }
        url = "{}{}".format(self.engine_url, endpoint)
        request_module = getattr(requests, method)
        try:
            json.update({
                "username": self.engine_user,
                "password": self.engine_password,
            })
            return request_module(url, headers=headers, json=json)
        except ConnectionError:
            response = Response()
            response.status_code = 400
            response.json = lambda: {}
            return response

    def score(self, policy, workflow, variables):
        return self.make_request("post", "/scores/", json={
            "policy": policy,
            "workflow": workflow,
            "variables": variables
        })
