from django.urls import path
from api.views import SnapshotCallbackView, HealthCheckView, ActiveWalletProcessCallbackView, LastDBInfoView, \
    ValidateAndAutoProcessView, ActiveWalletDownloadCallbackView, RunAutoProcessView


urlpatterns = [
    path('snapshot/callback/<int:snapshot_id>', SnapshotCallbackView.as_view(), name="snapshot_callback"),
    path('active_wallet/process/complete/<int:active_wallet_process_id>/<int:snapshot_id>/',
         ActiveWalletProcessCallbackView.as_view(), name="active_wallet_process_callback"),
    path('healthcheck', HealthCheckView.as_view(), name="healthcheck"),
    path('last_restore_db_info', LastDBInfoView.as_view(), name="last_restore_db_info"),
    path('validate_and_auto_process', ValidateAndAutoProcessView.as_view(), name="validate_and_auto_process"),
    path('active_wallet/download/callback', ActiveWalletDownloadCallbackView.as_view(), name="active_wallet_download_callback"),
    path('run_auto_process', RunAutoProcessView.as_view(), name="run_auto_process"),
]
