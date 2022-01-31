#!/usr/bin/env python3
import time, signal, sys, os
from absl import logging, app, flags

from cozify import hub, cloud
from cozify.Error import APIError

from prometheus_client import start_http_server, Summary, Counter, Gauge

FLAGS = flags.FLAGS

PREFIX = 'COZIFY_EXPORTER'

flags.DEFINE_integer('port', os.getenv(f'{PREFIX}_PORT', 9841), 'Port to serve data on')
flags.DEFINE_integer('interval', os.getenv(f'{PREFIX}_INTERVAL', 60), 'Interval in seconds for data polls')
flags.DEFINE_integer('tolerance_read', 10, 'How many consecutive read errors are fine', lower_bound=0)


# Define metrics
PREFIX = 'cozify_'
HUB_INFO = Gauge(PREFIX + 'hub_info', 'General Hub into', ['host', 'version', 'mac'])
DEVICE_INFO = Gauge(PREFIX + 'device_info', 'General device into', ['id', 'name'])

ACTIVE_POWER = Gauge(PREFIX + 'device_active_power', 'Current draw of power socket', ['id', 'name'])

def process_devices(devices):
    for device_id, device in devices.items():
        if 'activePower' in device['state']:
            ACTIVE_POWER.labels(
                id=device_id,
                name=device['name'],
                    ).set(device['state']['activePower'])



def main(argv):
    del argv
    error_counter_read = 0

    start_http_server(FLAGS.port)
    logging.info(f'Serving metrics at :{FLAGS.port}/metrics')

    while True:
        try:
            # Check hub & cloud connectivity and have it auto-renewed if it's deemed time to do so.
            hub.ping()
            # Cloud checking is needed since the loop will run for a long time unattended and cloud tokens expire
            # every 28 days.
            cloud.ping()

            # Get device data for all classes we currently support
            data = hub.devices(capabilities=[
                hub.capability.TEMPERATURE,
                hub.capability.HUMIDITY,
                hub.capability.ACTIVE_POWER,
                ])
        except APIError as e:
            error_counter_read += 1
            logging.error(f'Failed to get data({error_counter_read}/{FLAGS.tolerance_read}). Error code: {e.status_code}, error: {e}')
            if error_counter_read > FLAGS.tolerance_read:
                raise # Too many errors, let it burn to the ground
        else: # data retrieval succeeded
            error_counter_read = 0

        process_devices(data)

        time.sleep(FLAGS.interval)

def run():
    app.run(main)


if __name__ == "__main__":
    run()
