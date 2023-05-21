#!/usr/bin/env python3
from absl import logging

from prometheus_client import Summary, Counter, Gauge

PREFIX = 'cozify_'

LASTSEEN = Gauge(PREFIX + 'device_lastseen', 'Timestamp when device was last seen', ['id', 'name'])
LASTCHANGE = Gauge(PREFIX + 'device_lastchange', 'Timestamp when device state last changed', ['id', 'name'])
ACTIVE_POWER = Gauge(PREFIX + 'device_active_power', 'Current draw of power socket', ['id', 'name'])
ON_OFF = Gauge(PREFIX + 'device_on', 'If a device with an on/off state is on', ['id', 'name'])
REACHABLE = Gauge(PREFIX + 'device_reachable', 'If a device is reachable', ['id', 'name'])

state_metrics = {
    'lastSeen': LASTSEEN,
    'lastChange': LASTCHANGE,
    'reachable': REACHABLE,
    'activePower': ACTIVE_POWER,
    'isOn': ON_OFF
        }

def process_devices(devices):
    for device_id, device in devices.items():
        for state, metric in state_metrics.items():
            if state in device['state']:
                metric.labels(
                    id=device_id,
                    name=device['name'],
                        ).set(device['state'][state])
