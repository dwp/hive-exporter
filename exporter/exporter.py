import json
import time
import boto3
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import argparse
import yaml
from objectpath import Tree
import logging

DEFAULT_PORT=3392
DEFAULT_LOG_LEVEL='info'

class JsonPathCollector(object):
  def __init__(self, config):
    self._config = config
    self._s3_client = boto3.client("s3")

  def collect(self):
    config = self._config
    result = json.loads(response = self._s3_client.get_object(Bucket=config['metrics_bucket'], Key=config['metrics_key'])["Body"].read().decode("utf8"))
    result_tree = Tree(result)
    for metric_config in config['metrics']:
      metric_name = "{}_{}".format(config['metric_name_prefix'], metric_config['name'])
      metric_description = metric_config.get('description', '')
      metric_path = metric_config['path']
      value = result_tree.execute(metric_path)
      logging.debug("metric_name: {}, value for '{}' : {}".format(metric_name, metric_path, value))
      metric = GaugeMetricFamily(metric_name, metric_description, value=value)
      yield metric


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Expose metrics by jsonpath for configured url')
  parser.add_argument('config_file_path', help='Path of the config file')
  args = parser.parse_args()
  with open(args.config_file_path) as config_file:
    config = yaml.load(config_file)
    log_level = config.get('log_level', DEFAULT_LOG_LEVEL)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.getLevelName(log_level.upper()))
    exporter_port = config.get('exporter_port', DEFAULT_PORT)
    logging.debug("Config %s", config)
    logging.info('Starting server on port %s', exporter_port)
    start_http_server(exporter_port)
    REGISTRY.register(JsonPathCollector(config))
  while True: time.sleep(5)
