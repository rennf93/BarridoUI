from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from web.templatetags.webtags import get_applications_template


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_applications_template(self.request, True)
        return context


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    template_name = "change-password.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Se ha cambiado su contraseña")
        return super().form_valid(form)


