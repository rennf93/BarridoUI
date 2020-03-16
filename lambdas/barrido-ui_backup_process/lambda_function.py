from botocore.vendored import requests
import logging
import os
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Inicia ejecucion "Proceso CA auotmatico"...')

    url = get_url()

    logger.info('Proceso CA auotmatico URL:' + url)
    if url:
        headers={'Content-type': 'application/json'}
        logger.info('Request headers: ' + str(headers))
        response = requests.get(url, headers=headers)
        logger.info('Response Status Code: ' + str(response.status_code))
        logger.info('Response Text:' + response.text)
        logger.info('Ejecucion "Proceso CA auotmatico" finalizada')
        return 'OK'
    else:
        return 'OK sin URL'


def get_url():
    company = os.environ['COMPANY']
    env = os.environ['ENV']
    logger.info('Environment values, company={}, env={}'.format(company, env))
    url = ''
    if company.upper() == 'CAR':
        if env.upper() == 'STAGE':
            url = 'https://barridouipub.stage.fintechpeople.net/api/run_auto_process_'
        elif env.upper() == 'PROD':
            url = 'https://barridouipub.fintechpeople.net/api/run_auto_process'
    else:
        if env.upper() == 'STAGE':
            url = 'https://barridouipub.stage.fintechpeople.io/api/run_auto_process'
        elif env.upper() == 'PROD':
            url = 'https://barridouipub.fintechpeople.io/api/run_auto_process'
        else:
            # En DEV se pidió deshabilitar  para que no consuma créditos del server (se agrega el UNDERSCORE al final)
            url = 'https://barridouipub.dev.fintechpeople.io/api/run_auto_process_'
    logger.info('Return values, url={}'.format(url))
    return url
    