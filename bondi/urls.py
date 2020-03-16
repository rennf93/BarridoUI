from django.urls import path
from bondi.views import (TopicsView, SubscriberMessagesView, SubscriberMessagesDeleteView)

urlpatterns = [
    path('topics/', TopicsView.as_view(), name="topics"),
    path('subscriber_messages/', SubscriberMessagesView.as_view(), name="subscriber_messages"),
    path('delete_message/', SubscriberMessagesDeleteView.as_view(), name="delete_message"),
]
