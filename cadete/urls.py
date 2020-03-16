from django.urls import path
from cadete.views import (OperationsView, OperationsDetailView, DownloadOperationRenditionFileView,
                          DownloadOperationWarehouseFileView, ConfigurationsUpdateView, ConfigurationsView,
                          ConfigurationsDetailView, ConfigurationsCreateView, ConfigurationsCreateBankView,
                          ConfigurationsAltaBankView)

urlpatterns = [
    path('operations/', OperationsView.as_view(), name="operations"),
    path('operations/filter/<str:filter_name>/<str:filter_value>', OperationsView.as_view(), name="operations_filter"),
    path('operations/detail/<str:operation_id>', OperationsDetailView.as_view(), name="operations_detail"),
    path('operations/rendition_file/<str:operation_id>', DownloadOperationRenditionFileView.as_view(),
         name="operations_rendition_file"),
    path('operations/warehouse_file/<str:operation_id>/<str:warehouse_id>',
         DownloadOperationWarehouseFileView.as_view(), name="operations_warehouse_file"),
    path('configurations/<str:config_type>', ConfigurationsView.as_view(), name="configurations"),
    path('configurations/<str:config_type>/create', ConfigurationsCreateView.as_view(), name="configurations_create"),
    path('configurations/<str:config_type>/create/<str:bank_name>',
         ConfigurationsCreateBankView.as_view(), name="configurations_create_bank"),
    path('configurations/<str:config_type>/alta/<str:bank_name>',
         ConfigurationsAltaBankView.as_view(), name="configurations_alta_bank"),
    path('configurations/<str:config_type>/detail/<str:configuration_id>',
         ConfigurationsDetailView.as_view(), name="configurations_detail"),
    path('configurations/<str:config_type>/update/<str:configuration_id>',
         ConfigurationsUpdateView.as_view(), name="configurations_update")
]
