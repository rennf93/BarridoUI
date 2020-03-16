from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from risk.models import Score


class ScoreCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'risk.score_access'
    template_name = 'score/create.html'
    model = Score
    fields = ('data', 'policy', 'workflow')
    success_url = reverse_lazy('score_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super(ScoreCreateView, self).form_valid(form)


class ScoreListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'risk.score_access'
    template_name = "score/list.html"
    model = Score
    queryset = Score.objects.all().order_by("-created_at")
