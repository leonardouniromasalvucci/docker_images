#!/usr/bin/python3

import paho.mqtt.client as mqtt
import griddb_python as griddb
import pika, logging, os, sys, datetime, json, time, socket, subprocess, threading
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

try:
    machine_ip = os.environ['HOST_IP']
except:
    LOG.error('Error during the processing of the HOST IP')

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
                        conInfo = griddb.ContainerInfo(sub_topics[0]+"_"+sub_topics[1],
                                [["timestamp", griddb.Type.TIMESTAMP],
                                #["timestamp2", griddb.Type.TIMESTAMP],
                                ["sensorId", griddb.Type.STRING],
                                ["sensorValue", griddb.Type.STRING]],
                                griddb.ContainerType.TIME_SERIES, True)

                        col = gridstore.put_container(conInfo)
                        col.set_auto_commit(False)
                        #now = datetime.datetime.utcnow()
                        col.put([datetime.utcfromtimestamp(y["timestamp"]), str(y["device_id"]), str(y["value"])])
                        res = col.commit()
                        LOG.info("GridDB reply: " + str(res) + '.')
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
                client = mqtt.Client(client_id = machine_ip, clean_session = False)
                client.enable_logger(LOG)
                client.on_connect = on_connect
                client.on_message = on_message
                client.connect('InternalKalpaELB-c6dcbc9047674e10.elb.eu-west-1.amazonaws.com', 1883, 6)
                client.loop_forever()
                LOG.info('Connected to MQTT Brokers cluster.')
                break
        except:
                LOG.error("Connection error with MQTT Broker cluster. I'll try again...")
                time.sleep(2)
