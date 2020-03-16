from django.urls import path, include
from django.contrib.auth import views as auth_views

from web.templates.strategy.agents_data_views import AgentDataView
from web.views.active_wallet_process_views import ActiveWalletProcessListView, ActiveWalletProcessCreateView
from web.views.buckets_strategy_views import BucketsStrategiesView, BucketsStrategiesCreateView, \
    BucketsStrategiesImportView, BucketsStrategiesExportView, BucketsStrategiesDeleteView, BucketsStrategiesDetailView
from web.views.data_source_reader_settings_views import DataSourceReaderSettingsView
from web.views.index_views import IndexView, CustomPasswordChangeView
from web.views.outputs_strategy_views import OutputsStrategiesView, OutputsStratergiesDetailView
from web.views.paying_agents_strategy_views import (PayingAgentsStrategyView, PayingAgentsStratergiesDetailView)
from web.views.strategy_exec_views import StrategyExecutionsView, StrategyExecutionsExportView, \
    StrategyExecutionsDetailView, StrategyExecutionsNewView, StrategyExecutionsApproveView, \
    StrategyExecutionsCancelView, StrategyExecutionsApproveCancelAgentView, DownloadFileView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('change-password/', CustomPasswordChangeView.as_view(), name="password_change"),
    path('risk/', include("risk.urls")),
    path('middleware/', include("middleware.urls")),
    path('cadete/', include("cadete.urls")),
    path('cadetep/', include("cadetep.urls")),
    path('bondi/', include("bondi.urls")),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('buckets_strategy/<str:application>', BucketsStrategiesView.as_view(), name="buckets_strategy"),

    path('data_source_reader_settings/<str:application>', DataSourceReaderSettingsView.as_view(), name="data_source_reader_settings"),
    path('data_source_reader_settings/<str:data_source_reader_settings_id>/import', DataSourceReaderSettingsView.as_view(), name="data_source_reader_settings_import"),
    path('data_source_reader_settings/<str:data_source_reader_settings_id>/export', DataSourceReaderSettingsView.as_view(), name="data_source_reader_settings_export"),

    path('outputs_strategy/<str:application>', OutputsStrategiesView.as_view(), name="outputs_strategy"),
    path('outputs_strategy/<str:outputs_strategy_id>/detail', OutputsStratergiesDetailView.as_view(), name="outputs_strategy_detail"),

    path('buckets_strategy/create/<str:application>', BucketsStrategiesCreateView.as_view(), name="buckets_strategy_create"),
    path('buckets_strategy/<str:buckets_strategy_id>/detail', BucketsStrategiesDetailView.as_view(), name="buckets_strategy_detail"),
    path('buckets_strategy/<str:buckets_strategy_id>/import', BucketsStrategiesImportView.as_view(), name="buckets_strategy_import"),
    path('buckets_strategy/<str:buckets_strategy_id>/export', BucketsStrategiesExportView.as_view(), name="buckets_strategy_export"),
    path('buckets_strategy/<str:buckets_strategy_id>/delete', BucketsStrategiesDeleteView.as_view(), name="buckets_strategy_delete"),

    path('strategy_exec/<str:application>', StrategyExecutionsView.as_view(), name="strategy_exec"),
    path('strategy_exec/export/<str:strategy_exec_id>', StrategyExecutionsExportView.as_view(), name="strategy_exec_export"),
    path('strategy_exec/detail/<str:strategy_exec_id>', StrategyExecutionsDetailView.as_view(), name="strategy_exec_detail"),
    path('strategy_exec/<str:application>/process', StrategyExecutionsNewView.as_view(), name="strategy_exec_new"),
    path('strategy_exec/<str:strategy_exec_id>/approve', StrategyExecutionsApproveView.as_view(), name="strategy_exec_approve"),
    path('strategy_exec/<str:strategy_exec_id>/cancel', StrategyExecutionsCancelView.as_view(), name="strategy_exec_cancel"),
    path('strategy_exec/agent/<str:action_id>/<str:strategy_exec_id>/<str:agent_code>', StrategyExecutionsApproveCancelAgentView.as_view(), name="strategy_exec_approve_cancel_agent"),

    path('utils/download_file/<str:file_storage_key>', DownloadFileView.as_view(), name="download_file"),

    path('active_wallet/', ActiveWalletProcessListView.as_view(), name="active_wallet_process_list"),
    path('active_wallet/create/', ActiveWalletProcessCreateView.as_view(), name="active_wallet_process_create"),
    path('agents_data/', AgentDataView.as_view(), name="agents_data"),

    path('paying_strategy/<str:application>', PayingAgentsStrategyView.as_view(), name="paying_agents_strategy"),
    path('paying_strategy/<str:paying_agents_strategy_id>/detail', PayingAgentsStratergiesDetailView.as_view(), name="paying_agents_strategy_detail"),
    path('paying_strategy/<str:paying_agents_strategy_id>/import', PayingAgentsStratergiesDetailView.as_view(), name="paying_agents_strategy_import"),
    path('paying_strategy/<str:paying_agents_strategy_id>/export', PayingAgentsStratergiesDetailView.as_view(), name="paying_agents_strategy_export"),
]
