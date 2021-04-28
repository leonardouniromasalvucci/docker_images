#!/usr/bin/python3

import paho.mqtt.client as mqtt
import logging, os, sys, datetime, json, time, socket, subprocess, threading
from datetime import datetime
import argparse, requests

from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 
properties=Properties(PacketTypes.CONNECT)
properties.SessionExpiryInterval=1273


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

topic = '#'
col = None
factory = None
update = True
connected = False
broker = "InternetKalpaELB-5c0c715d50ed9d71.elb.eu-west-1.amazonaws.com"

client = None
mqtt.Client.connected_flag=False


def on_disconnect(client, userdata, rc):
        logging.info("disconnecting reason  "  +str(rc))
        #client.reconnect()

def on_connect(client, userdata, flags, reasonCode, properties=None):
        client.subscribe(topic, qos=2)
        LOG.info('MQTT subscriber is ready.')

def on_message(client, userdata, message):
        LOG.info('MQTT: ' + str(message.payload.decode("utf-8")))
        y = json.loads(str(message.payload.decode("utf-8")))
        print(y)
        requests.get('https://restalb-1562068755.eu-west-1.elb.amazonaws.com/increment', verify=False)

while True:
        LOG.info('Trying to connect to MQTT Broker cluster...')
        try:
                client = mqtt.Client(client_id="sub_test",  protocol = 5)
                client.enable_logger(LOG)
                client.on_connect = on_connect
                client.on_message = on_message
                client.on_disconnect = on_disconnect
                client.connect(host = broker, port = 1883, keepalive = 1200, clean_start=False, properties = properties)
                client.username_pw_set("dev-01", "dev-01234")
                client.loop_forever()
                LOG.info('Connected to MQTT Brokers cluster.')
                break
        except:
                LOG.error("Connection error with MQTT Broker cluster. I'll try again...")
                time.sleep(2)