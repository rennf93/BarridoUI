from django.conf.urls import url
from django.urls import path

from cadetep.views import (ManualCashinListView, ManualCashinCreateView)

urlpatterns = [
    path('manualcashins/',
         ManualCashinListView.as_view(), name="manualcashins"),
    path('manualcashins/create',
         ManualCashinCreateView.as_view(), name="manualcashins_create"),
    url('manualcashins/create/get_channels',
        ManualCashinCreateView.get_channels, name="manualcashins_create_get_channels"),
    url('manualcashins/create/get_agreements',
        ManualCashinCreateView.get_agreements, name="manualcashins_create_get_agreements")
]
