#!/usr/bin/python3

import paho.mqtt.client as mqtt
import logging, os, sys, datetime, json, time, socket, subprocess, threading
from datetime import datetime

from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 
properties=Properties(PacketTypes.CONNECT)
properties.SessionExpiryInterval=1273
import re



logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

topic = '$share/group1/#'
col = None
factory = None
update = True
connected = False
broker = "KalpaELB-10280071324ea8de.elb.eu-west-1.amazonaws.com"

client = None
mqtt.Client.connected_flag=False

def on_disconnect(client, userdata, rc):
        logging.info("Disconnecting reason " + str(rc))
        client.connected_flag = False

def on_connect(client, userdata, flags, reasonCode, properties=None):
        client.subscribe(topic, qos = 2)
        LOG.info('MQTT subscriber is ready.')
        if reasonCode == 0:
                client.connected_flag = True
        else:
                client.connected_flag = False

def on_message(client, userdata, message):
        LOG.info('MQTT: ' + str(message.payload.decode("utf-8")))
        y = json.loads(str(message.payload.decode("utf-8")))
        sub_topics = str(message.topic).split('/')[1:-1]
        print(sub_topics[0]+"_"+sub_topics[1])

while True:
        LOG.info('Trying to connect to MQTT Broker cluster...')
        try:
                client = mqtt.Client(client_id = "test_sub_last",  protocol = 5)
                client.enable_logger(LOG)
                client.on_connect = on_connect
                client.on_message = on_message
                client.on_disconnect = on_disconnect
                client.connect(host = broker, port = 1883, keepalive = 1200, clean_start = False, properties = properties)
                client.loop_forever()
                LOG.info('Connected to MQTT Brokers cluster.')
                break
        except:
                LOG.error("Connection error with MQTT Broker cluster. I'll try again...")
                time.sleep(2)