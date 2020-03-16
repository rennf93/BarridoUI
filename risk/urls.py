from django.urls import path
from risk.views import ScoreCreateView, ScoreListView

urlpatterns = [
    path('score/', ScoreListView.as_view(), name="score_list"),
    path('score/create', ScoreCreateView.as_view(), name="score_create"),
]
