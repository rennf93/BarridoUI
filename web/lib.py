import json
import operator
from django.contrib import messages

from core.core_barrido import CoreBarridoClient


def get_application_description(request, application_code=None):
    if application_code is None:
        return "Application not defined"
    if application_code in current_application_list(request):
        return [app for app in get_applications(request, False)
                if app.get("code") == application_code][0]["description"]
    else:
        return [app for app in get_applications(request, True)
                if app.get("code") == application_code][0]["description"]


def current_application_list(request):
    return list(map(operator.itemgetter('code'), get_applications(request, False)))


def get_applications(request, force_reload):
    if 'applications' in request.session and not force_reload:
        application_list = request.session["applications"]
    else:
        barrido_client = CoreBarridoClient()
        applications = barrido_client.get_applications()
        if applications.status_code == 200:
            application_list = applications.json()
        else:
            messages.add_message(request, messages.ERROR,
                                 f"Error de conexión: [{applications.status_code}]"
                                 f"{applications.text} "
                                 f"{applications.reason}")
            application_list = []
        request.session["applications"] = application_list
    return application_list


def has_access_to_app_element(element_name, app, current_user):
    return current_user.has_perm(F"core.{element_name}_access_{app}")


def get_response_message(response):
    parsed = json.loads(response.content)
    return parsed["message"]
