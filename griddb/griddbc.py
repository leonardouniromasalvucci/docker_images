#!/usr/bin/python3

import paho.mqtt.client as mqtt
import griddb_python as griddb
import pika, logging, os, sys, datetime, json, time

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

try:
        machine_ip = os.environ['RUBBITMQ_HOST_IP']
except:
        LOG.error('Error during the processing of the HOST IP')

col = None
factory = None

update = True
connected = False

LOG.info('Trying to connect to GridDB...')

while True:
        time.sleep(5)
        try:
                factory = griddb.StoreFactory.get_instance()
                gridstore = factory.get_store(
                notification_member="10.0.0.28:10001,10.0.0.37:10001,10.0.0.172:10001",
                cluster_name="defaultCluster",
                username="admin",
                password="admin")

                conInfo = griddb.ContainerInfo("SensorValuesKalpaLast",
                                [["timestamp", griddb.Type.TIMESTAMP],
                                ["sensorId", griddb.Type.STRING],
                                ["sensorValue", griddb.Type.STRING]],
                                griddb.ContainerType.TIME_SERIES, True)

                col = gridstore.put_container(conInfo)
                LOG.info('CONNECTED to GridDB.....')
                break

        except griddb.GSException as e:
                LOG.error('Error during connection to GridDB.....')


def callback(ch, method, properties, body):
        y = json.loads(str(body.decode()))
        LOG.info("Received %r" % y)
        #while True:
        #        time.sleep(1)
        #try:
        now = datetime.datetime.utcnow()
        res = col.put([now, str(y["device_id"]), str(y["value"])])
        LOG.info("GridDB reply: " + res)
        ch.basic_ack(delivery_tag=method.delivery_tag)
                #break
        #except:
        #        LOG.error("Error during update gridDB. I'll try again")

#while True:
#        time.sleep(5)
#        try:
connection = pika.BlockingConnection(pika.ConnectionParameters(host=machine_ip, port=5672))
channel = connection.channel()
channel.queue_declare(queue='kalpa_queue', durable=True)
LOG.info('Waiting for RubbitMQ messages.')
#channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='kalpa_queue', on_message_callback=callback)
channel.start_consuming()
LOG.info("RubbitMQ connection established.")
#                break
#        except:
#                LOG.error("Connection error with RubbitMQ server.")


