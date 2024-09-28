#!/usr/bin/env python3

# listens to IHC events and updates the HA switch and sensor states accordingly

import sys
import logging
import json
import yaml
import requests
import websocket
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from setproctitle import setproctitle

setproctitle('ihcclient')


def readYamlConfig(configfile):
    try:
        with open(configfile, 'r') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        sys.exit("Error: file '" + configfile + "' not found")
    except yaml.YAMLError as error:
        sys.exit(error)
    return None


# read main configuration file:
settings = readYamlConfig('settings.yaml')

ihc_server = settings['ihc']['server'] + ":" + str(settings['ihc']['port'])
ihc_username = settings['ihc']['username']
ihc_password = settings['ihc']['password']

hass_server = settings['hass']['server'] + ":" + str(settings['hass']['port'])
hass_token = settings['hass']['token']

log_file = settings['log_file']

# read IHC I/O configuration file:
pins = readYamlConfig('modules.yaml')

# set headers for HASS instance:
hass_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + hass_token
}

# map IHC states to HASS states:
states = {
    'True': 'on',
    'False': 'off'
}

# set up logging:
logging.basicConfig(filename=log_file,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
console = logging.StreamHandler()
logging.getLogger('').addHandler(console)


def setHAState(entity, state):
    # note that we must first get the attributes, otherwise they will get lost
    # if we later post only the state of the entity!
    response = session.get('http://' + hass_server + '/api/states/' + entity, headers=hass_headers, verify=False)
    json_data = response.json()
    # print(json_data)
    attributes = json_data['attributes']
    # print(attributes['friendly_name'])
    # now we can post state AND attributes:
    session.post('http://' + hass_server + '/api/states/' + entity, json={'attributes': attributes, 'state': state}, headers=hass_headers, verify=False)
    # logging.info('%s %s', entity, state)
    logging.info('%s - %s %s', attributes['friendly_name'], entity, state)
    # print()


def getIHCStates(moduleType):
    for module in initial_states['modules'][moduleType + 'Modules']:
        ioType = moduleType + 'State'
        if module['state'] is True:
            moduleNumber = module['moduleNumber']
            for state in module[moduleType + 'States']:
                ioNumber = state[moduleType + 'Number']
                pin = next((e for e in pins if (
                    e['type'] == ioType and
                    e['moduleNumber'] == moduleNumber and
                    e['ioNumber'] == ioNumber)
                ), False)

                if pin:
                    entity = pin['entity']
                    state = states.get(str(state[moduleType + 'State']))
                    # print(ioType, moduleNumber, ioNumber, entity, state)
                    setHAState(entity, state)


def createHTTPSession():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session


session = createHTTPSession()

# read initial states from IHC controller:
print("Reading initial IHC states...")
response = session.post('http://' + ihc_server + '/ihcrequest', json={'type': 'getAll'}, auth=(ihc_username, ihc_password))
initial_states = response.json()
# print(initial_states)

getIHCStates('input')
getIHCStates('output')

# wait for events over websocket
ws = websocket.create_connection('ws://' + ihc_server + '/ihcevents-ws')
print("Waiting for IHC events...")

try:
    while True:
        event = ws.recv()
        json_data = json.loads(event)
        # print("Received", json_data)

        ioType = json_data['type']
        if ioType == 'ping':
            ws.send(json.dumps({'type': 'pong'}))
            continue
        moduleNumber = json_data['moduleNumber']
        ioNumber = json_data['ioNumber']
        ioState = json_data['state']

        state = states.get(str(ioState))

        pin = next((e for e in pins if (
            e['type'] == ioType and
            e['moduleNumber'] == moduleNumber and
            e['ioNumber'] == ioNumber)
        ), False)

        if pin:
            entity = pin['entity']
            # print("Received ", moduleNumber, ioNumber, state)
            setHAState(entity, state)

except KeyboardInterrupt:
    print("\nClosing connection...")
except Exception as error:
    print("Error in WebSocket connection:", error)
finally:
    ws.close()
    print("Connection closed.")
