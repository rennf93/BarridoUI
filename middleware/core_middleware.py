import requests
import json
from requests.models import Response
from requests.exceptions import ConnectionError
from django.conf import settings
from core.utils import RequestUtils


class CoreMiddlewareClient(object):
    def __init__(self):
        self.middleware_url = getattr(settings, "CORE_MIDDLEWARE_URL")
        self.api_auth_token = getattr(settings, "CORE_MIDDLEWARE_API_AUTH_TOKEN")
        self.cashin_middleware_url = getattr(settings, "CORE_MIDDLEWARE_CASHIN_URL")
        self.cashin_api_auth_token = getattr(settings, "CORE_MIDDLEWARE_CASHIN_API_AUTH_TOKEN")

    def make_request(self, method, endpoint, files=None, data=None, json=None, add_headers=None, cashin=False):
        headers = {
            "x-api-auth-token": self.cashin_api_auth_token if cashin else self.api_auth_token,
            "Content-Type": "application/json",
        }
        if add_headers:
            headers.update(add_headers)

        url = "{}{}".format(self.cashin_middleware_url if cashin else self.middleware_url, endpoint)
        request_module = getattr(requests, method)
        try:
            if files:
                del headers["Content-Type"]
                return request_module(url, headers=headers, files=files, data=data)
            elif json:
                return request_module(url, headers=headers, json=json)
            else:
                return request_module(url, headers=headers, data=data)
        except ConnectionError:
            response = Response()
            response.status_code = 400
            response.json = lambda: {}
            return response

    def companies(self, user_filter=""):
        return self.validate_response(self.make_request("get", "/ui/companies" + user_filter))

    def get_company(self, company_id):
        return self.make_request("get", "/ui/companies/{}".format(company_id))

    def get_company_by_code(self, company_code):
        return self.make_request("get", "/ui/companies?companyCode={}".format(company_code))

    def get_banks_by_company(self, company_id):
        return self.make_request("get", "/ui/company/{}/bank".format(company_id))

    def banks(self):
        return self.validate_response(self.make_request("get", "/ui/bank?search=removedDate:null"))

    def get_company_bank(self, company_code, bank_code):
        return self.make_request("get", "/ui/company-bank/{}/{}".format(company_code, bank_code))

    def patch_company_bank(self, company_bank, company_code, bank_code, purge):
        purged_company = RequestUtils.purge_dictionary(company_bank, purge)
        return self.make_request("patch", "/ui/company-bank/{}/{}".format(company_code, bank_code),
                                 json=json.loads(json.dumps(purged_company)))

    def post_company_bank(self, company_bank, company_id, bank_code, purge):
        purged_company = RequestUtils.purge_dictionary(company_bank, purge)
        return self.make_request("post", "/ui/company-bank/{}/{}".format(company_id, bank_code),json=json.loads(json.dumps(purged_company)))

    def create_company(self, **kwargs):
        return self.make_request("post", "/ui/companies", json={
            "code": kwargs.pop("code"),
            "cuit": kwargs.pop("cuit"),
            "mambuUrl": kwargs.pop("mambu_url"),
            "mambuUser": kwargs.pop("mambu_user"),
            "mambuPass": kwargs.pop("mambu_pass"),
            "taxSourceKey": kwargs.pop("tax_source_key"),
            "timezone": kwargs.pop("timezone"),
            "picAvailable": kwargs.pop("pic_available"),
            "picKey": kwargs.pop("pic_key"),
            "picMaxAmount": kwargs.pop("pic_max_amount")
        })

    def update_company(self, **kwargs):
        return self.make_request("patch", "/ui/companies?code=" + kwargs.pop("code"), json={
            "cuit": kwargs.pop("cuit"),
            "taxSourceKey": kwargs.pop("tax_source_key"),
            "timezone": kwargs.pop("timezone"),
            "picAvailable": kwargs.pop("pic_available"),
            "picKey": kwargs.pop("pic_key"),
            "picMaxAmount": kwargs.pop("pic_max_amount")
        })

    def delete_company(self, company_id):
        return self.make_request("delete", "/ui/companies?code=" + company_id)

    # [Cash In]
    def cashin_process_status(self):
        return self.validate_response(self.make_request("get", "/ui/util/cashin-process-status", cashin=True))

    def cashin_generic_process(self, bank, consumer_username, file_contents, file_name):
        username_header = {
            "x-consumer-username": consumer_username,
        }
        return self.make_request(
            "post", "/cashin/async/{}".format(bank),
            files={
                "file": (file_name, file_contents)
            }
            , add_headers=username_header
            , cashin=True
        )

    @staticmethod
    def validate_response(response):
        if response.status_code != 200:
            response.json = lambda: {}
        return response

    # [Cash Out]
    def get_cash_out_summaries(self, filter):
        return self.make_request("get", "/ui/cashouts/summaries" + filter)

    def get_cash_outs_by_company_bank_sending_date(self, company_id, bank_id, sending_date, filter):
        return self.make_request("get", "/ui/cashouts/search?companyId={}&bankId={}&sendingDate={}".format(company_id, bank_id, sending_date) + filter)

    def get_cash_out_loans(self, cash_out_id, filter):
        return self.make_request("get", "/ui/cashouts/{}/loans".format(cash_out_id) + filter)

    def get_cash_out_refunds(self, cash_out_id, filter):
        return self.make_request("get", "/ui/cashouts/{}/refunds".format(cash_out_id) + filter)

    def download_cash_out_summarie(self, company_id, bank_id = None, sending_date = None):
        filter  = ""
        if bank_id:
            filter = filter + "&bankId={}".format(bank_id)
        if sending_date:
            filter = filter + "&date={}".format(sending_date)

        return self.make_request("get", "/ui/cashouts/summaries/download?companyId={}".format(company_id) + filter)

    def get_cash_in_binnacle_summaries(self):
        return self.make_request("get", "/ui/cashin/binnacle/summaries")

    def get_cash_in_binnacle_summaries_download(self, binnacle_date):
        return self.make_request("get", "/ui/cashin/binnacle/summaries/download?date={}".format(binnacle_date.replace("-", "")))

    def patch_products_order(self, sorted_products, company_id):
        return self.make_request("patch", "/ui/cashouts/disbursement/priority", json={
            "sorted_products": sorted_products,
            "company_id": company_id
        })

    def get_sorted_products(self, company_id):
        return self.make_request("get", "/ui/cashouts/disbursement/priority/{}/company".format(company_id))
