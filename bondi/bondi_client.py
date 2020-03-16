import requests
from requests.models import Response
from django.conf import settings


class BondiClient(object):

    def __init__(self):
        self.bondi_url = getattr(settings, "BONDI_URL")
        self.x_publish_token_ca_report = getattr(settings, "BONDI_XPUBTOKEN_CA_REPORT")

    def make_request(self, method, endpoint, files=None, data=None, json=None, add_headers=None):
        headers = {
            "Content-Type": "application/json",
        }
        if add_headers:
            headers.update(add_headers)

        url = "{}{}".format(self.bondi_url, endpoint)
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

    def get_topics(self):
        return self.make_request("get", "/topics")

    def get_messages(self, subscriber):
        return self.make_request("get", "/messages?max_messages=10&subscriber={}".format(subscriber))

    def delete_message(self, subscriber, message_id, delete_token):
        return self.make_request("delete", "/messages",
            json={
                "subscriber": subscriber,
                "messages": [{"message_id": message_id, "delete_token": delete_token}]
        })

    def pub_message(self, x_publish_token, topic, message):
        x_publish_token_header = {
            "X-Publish-Token": x_publish_token,
        }
        return self.make_request("post", "/messages",
            json={
                "topic": topic,
                "payload": message
            }, add_headers=x_publish_token_header)
