import requests
import sys
from requests.models import Response
from requests.exceptions import ConnectionError
from django.conf import settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class NotificationClient(object):
    def __init__(self):
        self.notification_url = getattr(settings, "NOTIFICATION_URL")
        self.generic_id = getattr(settings, "NOTIFICATIONS_MESSAGE_TPL_ID")
        self.generic_to = getattr(settings, "NOTIFICATION_GENERIC_TO")

    def make_request(self, method, endpoint, files=None, data=None, json=None):
        headers = {
            "Content-Type": "application/json",
        }
        url = "{}{}".format(self.notification_url, endpoint)
        request_module = getattr(requests, method)
        try:
            logger.info("notification: {}".format(url))
            logger.info("payload: {}".format(json))
            if files:
                return request_module(url, files=files, data=data)
            return request_module(url, headers=headers, json=json)
        except Exception as error:
            logger.error(error)
            response = Response()
            response.status_code = 400
            response.json = lambda: {}
            return response

    def send_generic(self, message):
        return self.make_request(
            "post", "/notifications/",
            json={
                "notification_id": self.generic_id,
                "to": [self.generic_to],
                "data": {"message": message}
            }
        )




