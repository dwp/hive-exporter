import os
import threading
import time
import yaml
import socket
import boto3
import json
import requests
from jsonpath_ng import jsonpath, parse
from prometheus_client import Gauge, REGISTRY, start_http_server

metrics = {}
paths = {}
config = {}
s3_client = boto3.client("s3")
emr_client = boto3.client("emr")

def scrape_http():
    clusters = emr_client.list_clusters(ClusterStates=('STARTING','BOOTSTRAPPING','RUNNING','WAITING'))
    for cluster in clusters['Clusters']:
        if cluster['Name'] == config['cluster_name']:
            hostname = emr_client.describe_cluster(ClusterId=cluster['Id'])['Cluster']['MasterPublicDnsName']
    response = requests.get("http://" + hostname + "/jmx")
    return response.json()
  
def scrape_s3():
    bucket = config['metrics_bucket']
    key = config['metrics_key']
    json_file = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf8")
    return json.loads(json_file)

def collect(): 
    for metric_config in config['metrics']:
        metric_name = "{}_{}".format(config['metric_name_prefix'], metric_config['name'])
        metric_description = metric_config.get('description', '')
        metrics[metric_name] = Gauge(metric_name, metric_description)
        paths[metric_name] = metric_config['path']

def gather_data():
    collect()
    while True:
        time.sleep(5)
        if 'metrics_bucket' in config:
            result = scrape_s3()
        else:
            result = scrape_http()
        for metric in metrics:
            value = parse(paths[metric]).find(result)
            if not bool(value):
                continue
            print(metric + ": " + str(value[0].value))
            value = value[0].value
            metrics[metric].set(value)

if __name__ == "__main__":
    with open(os.getenv("CONFIG_PATH", "config.yml")) as config_file:
        config = yaml.load(config_file)
    thread = threading.Thread(target=gather_data)
    thread.start()
    try:
        start_http_server(os.getenv("PORT_NUMBER", 3392))
    except KeyboardInterrupt:
        server.socket.close()
        thread.join()
