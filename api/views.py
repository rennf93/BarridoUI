from django.shortcuts import get_object_or_404
from rest_framework import views, status, generics
from rest_framework.response import Response
from core.models import (Snapshot, ActiveWalletProcess, SnapshotRestore, ActiveWalletReport)
from core.tasks import download_snapshot_task, ActiveWalletCompleteProcess, validate_and_auto_process_task, \
    active_wallet_report_callback_task, run_auto_process_task
from .serializers import SnapshotRestoreLastSerializer
import json

class SnapshotCallbackView(views.APIView):
    def dispatch(self, request, snapshot_id, *args, **kwargs):
        self.snapshot = get_object_or_404(Snapshot, id=snapshot_id)
        return super(SnapshotCallbackView, self).dispatch(request, snapshot_id, *args, **kwargs)

    def post(self, request, format=None):
        download_snapshot_task.delay(self.snapshot.id)
        return Response(status=status.HTTP_200_OK)


class ActiveWalletProcessCallbackView(views.APIView):
    def dispatch(self, request, active_wallet_process_id, snapshot_id, *args, **kwargs):
        self.active_wallet_process = get_object_or_404(ActiveWalletProcess, id=active_wallet_process_id)
        self.snapshot = get_object_or_404(Snapshot, id=snapshot_id)
        return super(ActiveWalletProcessCallbackView, self).dispatch(request, snapshot_id, *args, **kwargs)

    def post(self, request, format=None):
        ActiveWalletCompleteProcess().delay(self.active_wallet_process.id, self.snapshot.id)
        return Response(status=status.HTTP_200_OK)


class HealthCheckView(views.APIView):
    def get(self, request, format=None):
        return Response(status=status.HTTP_200_OK)


class LastDBInfoView(generics.RetrieveAPIView):
    serializer_class = SnapshotRestoreLastSerializer
    model = SnapshotRestore

    def get_object(self):
        queryset = self.model.objects.filter(status="finished")
        return queryset.last()


class ValidateAndAutoProcessView(views.APIView):
    def get(self, request, format=None):
        validate_and_auto_process_task.delay()
        return Response(status=status.HTTP_200_OK)


class RunAutoProcessView(views.APIView):
    def get(self, request, format=None):
        run_auto_process_task.delay()
        return Response(status=status.HTTP_200_OK)


class ActiveWalletDownloadCallbackView(views.APIView):
    def __init__(self):
        self.topic = None
        self.active_wallet_report = None
        self.active_wallet_report_url = None
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        self.topic = json.loads(request.body)['topic']
        if self.topic != 'test_topic':
            active_wallet_report_id = json.loads(request.body)['payload']['active_wallet_report_id']
            self.active_wallet_report = get_object_or_404(ActiveWalletReport, id=active_wallet_report_id)
            self.active_wallet_report_url = json.loads(request.body)['url']
        return super(ActiveWalletDownloadCallbackView, self).dispatch(request, *args, **kwargs)

    def post(self, request, format=None):
        if self.topic != 'test_topic':
            active_wallet_report_callback_task.delay(self.active_wallet_report.id, self.active_wallet_report_url)
        return Response(status=status.HTTP_200_OK)
