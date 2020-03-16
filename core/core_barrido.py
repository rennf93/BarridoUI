import requests
from requests.models import Response
from django.conf import settings


class CoreBarridoClient(object):
    def __init__(self):
        self.barrido_url = getattr(settings, "CORE_BARRIDO_URL")
        self.barrido_api_token = getattr(settings, "CORE_BARRIDO_API_TOKEN")
        self.company_cuit = getattr(settings, "COMPANY_CUIT")
        self.company_name = getattr(settings, "COMPANY_NAME")

    def make_request(self, method, endpoint, files=None, data=None, json=None):
        headers = {
            "Content-Type": "application/json",
            "x-api-auth-token" : self.barrido_api_token
        }
        url = "{}{}".format(self.barrido_url, endpoint)
        request_module = getattr(requests, method)
        try:
            if files:
                del headers["Content-Type"]
                return request_module(url, headers=headers, files=files, data=data)
            return request_module(url, headers=headers, json=json)
        except Exception:
            response = Response()
            response.status_code = 400
            response.json = lambda: {}
            return response

    def get_application(self, application):
        return self.make_request("get", "/application/code/{}".format(application))

    def get_applications(self):
        return self.make_request("get", "/application/")

    def get_data_source_reader_settings(self, application):
        return self.make_request("get", "/data_source_reader_settings/?application={}".format(application))

    def get_outputs_strategies(self, outputs_strategy_id):
        return self.make_request("get", "/outputs_strategies/{}".format(outputs_strategy_id))

    def data_source_reader_settings(self, application):
        return self.make_request("get", "/data_source_reader_settings/?application={}".format(application))

    def outputs_strategies(self, application):
        return self.make_request("get", "/outputs_strategies/?application={}".format(application))

    def buckets_strategies(self, application):
        return self.make_request("get", "/buckets_strategies/?application={}".format(application))

    def get_buckets_strategy(self, buckets_strategy_id):
        return self.make_request("get", "/buckets_strategies/{}".format(buckets_strategy_id))

    def export_buckets_strategy(self, buckets_strategy_id):
        return self.make_request("get", "/buckets_strategies/{}/download".format(buckets_strategy_id))

    def import_buckets_strategy(self, buckets_strategy_id, file):
        return self.make_request(
            "post", "/buckets_strategies/{}/import".format(buckets_strategy_id),
            files={
                "file": file
            }
        )

    def create_buckets_strategy(self, application, description):
        return self.make_request("post", "/buckets_strategies/", json={
            "application": application,
            "description": description,
        })

    def delete_buckets_strategy(self, buckets_strategy_id):
        return self.make_request("delete", "/buckets_strategies/{}".format(buckets_strategy_id))

    def process_active_wallet(self, application, 
                data_source_reader_settings_id, buckets_strategy_id, paying_agents_strategy_id, outputs_strategy_id,
                active_wallet, expired_date, pay_date, process_date, 
                start_collection_date, middle_collection_date, end_collection_date, username):
        return self.make_request(
            "post", "/active_portfolio/process/{}".format(buckets_strategy_id),
            files={
                "file": active_wallet
            },
            data={
                "application": application,
                "dataSourceReaderSettingsId": data_source_reader_settings_id,
                "bucketStrategyId": buckets_strategy_id,
                "payingAgentsStrategyId": paying_agents_strategy_id,
                "outputStrategyId": outputs_strategy_id,
                "expiredDate": expired_date,
                "payDate": pay_date,
                "processDate": process_date,
                "startCollectionDate": start_collection_date,
                "middleCollectionDate": middle_collection_date,
                "endCollectionDate": end_collection_date,
                "user" : username,
                "companyCuit" : self.company_cuit,
                "companyName" : self.company_name
            }
        )

    def strategy_executions(self, application):
        return self.make_request("get", "/strategy_executions/?application={}".format(application))

    def get_strategy_executions(self, strategy_execution_id):
        return self.make_request("get", "/strategy_executions/{}".format(strategy_execution_id))

    def export_strategy_executions(self, strategy_execution_id):
        return self.make_request("get", "/strategy_executions/{}/download".format(strategy_execution_id))

    def update_strategy_executions(self, strategy_execution_id, update_data):
        return self.make_request("patch", "/strategy_executions/{}".format(strategy_execution_id), json=update_data)

    def download_file_storage(self, file_storage_key):
        return self.make_request("get", "/utils/download/{}".format(file_storage_key))

    def paying_agents_strategies(self, application):
        return self.make_request("get", "/paying_agents_strategies/?application={}".format(application))

    def get_paying_agents_strategies(self, paying_agents_strategy_id):
        return self.make_request("get", "/paying_agents_strategies/{}".format(paying_agents_strategy_id))

    def agents_data(self):
        return self.make_request("get", "/agents_data/")

    def get_agent_data(self, agent_data_id):
        return self.make_request("get", "/agents_data/{}".format(agent_data_id))

    def approve_strategy_executions_agent(self, strategy_execution_id, agent_code):
        return self.make_request("post", "/jobs/syncprocesses/strategyexecutionapproval", 
            json={
                "strategyProcessExecutionId": strategy_execution_id,
                "agentCode": agent_code
        })

    def cancel_strategy_executions_agent(self, strategy_execution_id, agent_code):
        return self.make_request("post", "/jobs/syncprocesses/strategyexecutioncancellation", 
            json={
                "strategyProcessExecutionId": strategy_execution_id,
                "agentCode": agent_code
        })

    def account_block_import_process(self):
        return self.make_request("post", "/jobs/asyncprocesses/accountblockimport", 
            json={
                "caller_process_id": "barrido_ui"
        })

    def get_system_status_report(self):
        return self.make_request("get", "/system_status_report")
