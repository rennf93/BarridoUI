from django.shortcuts import render
from django.views.generic.base import RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from bondi.bondi_client import BondiClient
from django.contrib import messages
from core.parsers import datetime_parser

# Topics
class TopicsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.bondi_access'
    template_name = "bondi/topics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bondi_client = BondiClient()
        topics = bondi_client.get_topics()
        if topics:
            context["topics"] = topics.json(object_hook=datetime_parser)
        else:
            messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                        .format(topics.status_code, topics.reason))        
        return context

# Messages
class SubscriberMessagesView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.bondi_access'
    template_name = "bondi/subscriber_messages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_box = self.request.GET.get("search_box")
        if search_box:
            context["subscriber_id"] = search_box
            bondi_client = BondiClient()
            subscriber_messages = bondi_client.get_messages(search_box)
            if subscriber_messages:
                context["subscriber_messages"] = subscriber_messages.json(object_hook=datetime_parser)
            else:
                messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                            .format(subscriber_messages.status_code, subscriber_messages.reason))        
        return context

class SubscriberMessagesDeleteView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'core.bondi_access'
    template_name = "bondi/subscriber_messages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bondi_client = BondiClient()

        subscriber = self.request.GET.get("s")
        message_id = self.request.GET.get("m")
        delete_token = self.request.GET.get("t")

        context["subscriber_id"] = subscriber

        deleted = bondi_client.delete_message(subscriber, message_id, delete_token)
        if deleted:
            messages.add_message(self.request, messages.SUCCESS, "Mensaje borrado correctamente")        
            if subscriber:
                subscriber_messages = bondi_client.get_messages(subscriber)
                if subscriber_messages:
                    context["subscriber_messages"] = subscriber_messages.json(object_hook=datetime_parser)
                else:
                    messages.add_message(self.request, messages.ERROR, "Error al leer tabla: [{}] {}"
                                .format(subscriber_messages.status_code, subscriber_messages.reason))        
        else:
            messages.add_message(self.request, messages.ERROR, "Error al borrar el mensaje: [{}] {}"
                        .format(deleted.status_code, deleted.reason))        
                
        return context

