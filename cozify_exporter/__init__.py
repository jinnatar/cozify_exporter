#!/usr/bin/env python3
import time, signal, sys, os
from absl import logging, app, flags

from cozify import hub, cloud, hub_api
from cozify.Error import APIError

from prometheus_client import start_http_server, Info, Counter, Gauge

from cozify_exporter.device_metrics import process_devices

FLAGS = flags.FLAGS

PREFIX = 'COZIFY_EXPORTER'

flags.DEFINE_integer('port', os.getenv(f'{PREFIX}_PORT', 9841), 'Port to serve data on')
flags.DEFINE_integer('interval', os.getenv(f'{PREFIX}_INTERVAL', 60), 'Interval in seconds for data polls')
flags.DEFINE_integer('tolerance_read', 10, 'How many consecutive read errors are fine', lower_bound=0)


# Define top level metrics
PREFIX = 'cozify_'
HUB_INFO = Info(PREFIX + 'hub_info', 'General Hub into')
ERRORS_CONSECUTIVE = Gauge(PREFIX + 'errors_consecutive', 'Data fetch errors in a row')
ERRORS_TOTAL = Counter(PREFIX + 'errors_total', 'Data fetch errors in total')
QUERY_TOTAL = Counter(PREFIX + 'query_total', 'Data fetches performed in total')


def main(argv):
    del argv
    error_counter_read = 0

    start_http_server(FLAGS.port)
    logging.info(f'Serving metrics at :{FLAGS.port}/metrics')
    ERRORS_CONSECUTIVE.set(0)

    while True:
        try:
            # Check hub & cloud connectivity and have it auto-renewed if it's deemed time to do so.
            hub.ping()
            # Cloud checking is needed since the loop will run for a long time unattended and cloud tokens expire
            # every 28 days.
            cloud.ping()

            hub_id = hub.default()
            host = hub.host(hub_id)
            info = hub_api.hub(host=host)
            HUB_INFO.info({
                'id': hub_id,
                'host': host,
                'name': info['name'],
                'version': info['version']
                })

            devices = hub.devices()
        except APIError as e:
            error_counter_read += 1
            ERRORS_CONSECUTIVE.inc()
            ERRORS_TOTAL.inc()
            logging.error(f'Failed to get data({error_counter_read}/{FLAGS.tolerance_read}). Error code: {e.status_code}, error: {e}')
            if error_counter_read > FLAGS.tolerance_read:
                raise # Too many errors, let it burn to the ground
        else: # data retrieval succeeded
            error_counter_read = 0
            ERRORS_CONSECUTIVE.set(0)

        process_devices(devices)

        QUERY_TOTAL.inc()
        time.sleep(FLAGS.interval)

def run():
    app.run(main)


if __name__ == "__main__":
    run()
