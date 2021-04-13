#!/usr/bin/python3

import paho.mqtt.client as mqtt
import griddb_python as griddb
import pika, logging, os, sys, datetime, json, time, socket, subprocess, threading
from datetime import datetime

from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 
properties=Properties(PacketTypes.CONNECT)
properties.SessionExpiryInterval=1273

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

try:
    machine_ip = os.environ['HOST_IP']
except:
    LOG.error('Error during the processing of the HOST IP')

broker = "InternalKalpaELB-c6dcbc9047674e10.elb.eu-west-1.amazonaws.com"
topic = '$share/group1/#'
col = None
factory = None
update = True
connected = False

def on_disconnect(client, userdata, rc):
        sys.exit()

def on_connect(client, userdata, flags, rc):
        client.subscribe(topic, qos=2)
        LOG.info('MQTT subscriber ' + str(machine_ip) + ' is ready.')

def on_message(client, userdata, message):
        LOG.info('MQTT: ' + str(message.payload.decode("utf-8")))
        y = json.loads(str(message.payload.decode("utf-8")))
        sub_topics = str(message.topic).split('/')[1:-1]
        while True:
                LOG.info('Try insertion of message: ' + str(message.payload.decode("utf-8")) + ' in GridDB...')
                try:
                        conInfo = griddb.ContainerInfo("home-"+sub_topics[0]+"_device-"+sub_topics[1],
                                [["timestamp", griddb.Type.TIMESTAMP],
                                #["timestamp2", griddb.Type.TIMESTAMP],
                                ["label", griddb.Type.STRING],
                                ["value", griddb.Type.STRING]],
                                griddb.ContainerType.TIME_SERIES, True)

                        col = gridstore.put_container(conInfo)
                        col.set_auto_commit(True)
                        #now = datetime.datetime.utcnow(), str(y["device_id"])
                        r = col.put([datetime.utcfromtimestamp(y["timestamp"]), str(y["label"]), str(y["value"])])
                        LOG.info("GridDB reply: " + str(r) + '.')
                        break
                except:
                        LOG.error("Error during update GridDB cluster.")


while True:
        LOG.info('Trying to connect to GridDB cluster...')
        try:
                factory = griddb.StoreFactory.get_instance()
                gridstore = factory.get_store(
                notification_member="10.0.0.28:10001,10.0.0.37:10001,10.0.0.172:10001",
                cluster_name="defaultCluster",
                username="admin",
                password="admin")

                LOG.info('Connected to GridDB cluster.')
                break

        except griddb.GSException as e:
                LOG.error("Error during connection to GridDB cluster. I'll try again...")
                time.sleep(2)
        
while True:
        LOG.info('Trying to connect to MQTT Broker cluster...')
        try:
                client = mqtt.Client(client_id = machine_ip,  protocol = 5)
                client.enable_logger(LOG)
                client.on_connect = on_connect
                client.on_message = on_message
                client.connect(host = broker, port = 1883, keepalive = 1200, clean_start = False, properties = properties)
                client.loop_forever()
                LOG.info('Connected to MQTT Brokers cluster.')
                break
        except:
                LOG.error("Connection error with MQTT Broker cluster. I'll try again...")
                time.sleep(2)
