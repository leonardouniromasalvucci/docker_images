import pika, logging, sys, os, socket, time, subprocess
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

try:
    mqtt_id = os.environ['RUBBITMQ_HOST_IP']
except:
    LOG.error('Error during the processing of the HOST IP')

topic = '$share/group1/0001/'
broker = 'InternalKalpaELB-c6dcbc9047674e10.elb.eu-west-1.amazonaws.com'

from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 
properties=Properties(PacketTypes.CONNECT)
properties.SessionExpiryInterval=1273

channel = None
q_name = None
rabbit_queue = None
MAX_MESSAGES = 6

client = None
mqtt.Client.connected_flag = False

def on_disconnect(client, userdata, rc):
    logging.info("Disconnecting reason  "  + str(rc))
    client.connected_flag = False

def on_connect(client, userdata, flags, reasonCode, properties=None):
    if reasonCode==0:
            client.connected_flag = True
            client.subscribe(topic, qos=2)
            LOG.info('MQTT subscriber is ready.')
    else:
            client.connected_flag = False
            LOG.info('Connection error.')

def on_message(client, userdata, message):
    LOG.info('MQTT: ' + str(message.payload.decode("utf-8")))
    try:
        rabbit_queue = channel.queue_declare(queue='kalpa_queue', durable=True)
        LOG.info(rabbit_queue.method.message_count)
        channel.basic_publish(
            exchange='',
            routing_key='kalpa_queue',
            body=str(message.payload.decode("utf-8")),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        if(int(rabbit_queue.method.message_count) >= (MAX_MESSAGES-1)):
            client.disconnect()

    except:
        LOG.error('Error during update RubbitMQ queue.')
        sys.exit()

LOG.info('Starting connection with RubbitMQ server...')
while True:
    time.sleep(5)
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = mqtt_id, port = 5672))
        channel = connection.channel()
        break
    except:
        LOG.error('Connection error with RubbitMQ server.')
        sys.exit()
LOG.info('RubbitMQ connection established.')

LOG.info('Starting connection with MQTT Broker...')
while True:
    time.sleep(5)
    try:
        client = mqtt.Client(client_id = mqtt_id, protocol=5)
        client.enable_logger(LOG)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.connect(host = broker, port = 1883, keepalive = 1200, clean_start=False, properties = properties)
        client.loop_start()
        while(not client.connected_flag):
            pass
        break
    except:
        LOG.error('Connection error with MQTT Broker.')
        sys.exit()


while(True):
    if(client.connected_flag==False):
        rabbit_queue = channel.queue_declare(queue='kalpa_queue', durable=True)
        if(int(rabbit_queue.method.message_count) <= (MAX_MESSAGES/2)):
            client.loop_stop()
            client.reconnect()
            client.loop_start()
            
    time.sleep(1)