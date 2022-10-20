#!/usr/bin/env python3

import logging
import time
import requests
import os
from kubernetes import client, config, watch


VERSION = '0.0.1'
CLUSTER_NAME = os.getenv('CLUSTER_NAME')
API_KEY = os.getenv('API_KEY')
WAIT_TIME = 300


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info('Starting...')

    logger.info('Loading Kubernetes Config')

    config.load_incluster_config()

    api_client = client.ApiClient()
    api_instance = client.CoreV1Api(api_client)

    while True:
        logger.info('Listing ingresses')
        pods_response = api_instance.list_pod_for_all_namespaces()
        
        images = set()
        for pod in pods_response.items:
            for container in pod.spec.containers:
                logger.info(f'Image found: {container.image}')
                images.add(container.image)

        logger.info('Listing containers done')
        logger.info(images)

        try:
            r = requests.post(
                'https://imageregistrycleaner.api.apocode.io/api/v1/identity/integrations/kubernetes/callback',
                json={
                    'kubernetes_cluster_name': os.getenv('CLUSTER_NAME'),
                    'kubernetes_data': list(images),
                    'kubernetes_integration_version': VERSION,
                },
                headers = {
                    'X-Apo-Api-Key': os.getenv('API_KEY'),
                }
            )
            logger.info(r.json())
            r.raise_for_status()

            logger.info(f'Done!')

        except Exception as e:
            logger.error(e)
            logger.info(f'Failed. See error above.')


        logger.info(f'Waiting {WAIT_TIME} second before next update...')
        time.sleep(300)
        
