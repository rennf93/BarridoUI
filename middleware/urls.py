from django.urls import path
from middleware.views import (CompaniesView, CompaniesCreateView, CompaniesUpdateView, CompaniesDeleteView, BanksView,
                              BankFilterView, CompanyBankEdit, CompanyBankPatch, CompanyBankConfig,
                              CompanyBankConfigView, CashOutSummariesView, CashOutPrioritiesView, CashOutPrioritiesUpdate,
                              CashOutsByCompanyBankSendingDateView,CashOutLoansView, CashOutRefundsView, CashinProcessStatusView, CashInBinnacleSummaryView,
                              CashInBinnacleDownloadFileView, DownloadCashOutSummaryFileView)

urlpatterns = [
    path('companies/', CompaniesView.as_view(), name="companies"),
    path('companies/create', CompaniesCreateView.as_view(), name="companies_create"),
    path('companies/<str:company_id>/delete', CompaniesDeleteView.as_view(), name="companies_delete"),
    path('companies/<str:company_id>/update', CompaniesUpdateView.as_view(), name="companies_update"),
    path('banks/', BanksView.as_view(), name="banks"),
    path('banks/filter/<str:company_id>', BankFilterView.as_view(), name="bank_filter"),
    path('banks/edit/<str:company_code>/<str:bank_code>', CompanyBankEdit.as_view(), name="company_bank_edit"),
    path('banks/edit/send', CompanyBankPatch.as_view(), name="company_bank_edit_send"),
    path('banks/config/send', CompanyBankConfigView.as_view(), name="company_bank_config_send"),
    path('banks/config/<str:company_id>', CompanyBankConfig.as_view(), name="company_bank_config"),
    path('cashoutsummaries', CashOutSummariesView.as_view(), name="cash_out_summaries"),
    path('cashoutpriorities', CashOutPrioritiesView.as_view(), name="cash_out_priorities"),
    path('cashoutpriorities/update/<str:company_id>', CashOutPrioritiesUpdate.as_view(), name="cash_out_priorities_update"),
    path('cashouts', CashOutsByCompanyBankSendingDateView.as_view(), name="cash_outs"),
    path('cashouts/<str:cash_out_id>/loans', CashOutLoansView.as_view(), name="cash_out_loans"),
    path('cashouts/<str:cash_out_id>/refunds', CashOutRefundsView.as_view(), name="cash_out_refunds"),
    path('cashouts/summary/download', DownloadCashOutSummaryFileView.as_view(), name="cash_outs_summary_download"),
    path('cashin_process_status', CashinProcessStatusView.as_view(), name="cashin_process_status"),
    path('cashin_binnacle_summary', CashInBinnacleSummaryView.as_view(), name="cashin_binnacle_summary"),
    path('cashin_binnacle_summary/download/<str:binnacle_date>', CashInBinnacleDownloadFileView.as_view(), name="cashin_binnacle_download"),
]
