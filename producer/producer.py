import pika, logging, sys, os, socket, time, subprocess
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

try:
    bashCommandName = 'echo $NAME'
    output = subprocess.check_output(['bash','-c', bashCommandName]) 
    local_ip = socket.gethostbyname(socket.gethostname())
    machine_ip = os.environ['RUBBITMQ_HOST_IP']
    mqtt_id = machine_ip+''+ output
    LOG.error('The MQTT id is: ' + str(mqtt_id))
except:
    LOG.error('Error during the processing of the HOST IP')

topic = '$share/group1/0001/'

channel = None
q_name = None
rabbit_queue = None
MAX_MESSAGES = 10


'''
CHECK CONNECTION FOR EACH RECEIVED MESSAGE, IF NOT RECONNECT 
try:
  connection = pika.BlockingConnection(parameters)
  if connection.is_open:
    print('OK')
    connection.close()
    exit(0)
except Exception as error:
  print('Error:', error.__class__.__name__)
  exit(1)
'''


def on_connect(client, userdata, flags, rc):
    client.subscribe(topic, qos=2)
    LOG.info('MQTT: Process is connected and it is ready to subscribe.')

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
            client.unsubscribe(topic)
            while True:
                time.sleep(1)
                LOG.info('Waiting for publishing...')
                rabbit_queue = channel.queue_declare(queue='kalpa_queue', durable=True)
                if(int(rabbit_queue.method.message_count) <= (MAX_MESSAGES/2)):
                    client.subscribe(topic, qos=2)
                    break
    except:
        LOG.error('Error during update RubbitMQ queue.')
        sys.exit()



LOG.info('Starting connection with RubbitMQ server...')
while True:
    time.sleep(5)
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=machine_ip, port=5672))
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
        client = mqtt.Client(client_id = mqtt_id, clean_session = False)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect('InternalKalpaELB-c6dcbc9047674e10.elb.eu-west-1.amazonaws.com')
        client.loop_forever()
        break
    except:
        LOG.error('Connection error with MQTT Broker.')
        sys.exit()