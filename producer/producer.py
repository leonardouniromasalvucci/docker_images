import pika, logging, sys, os, socket, time
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

try:
    local_ip = socket.gethostbyname(socket.gethostname())
    machine_ip = os.environ['RUBBITMQ_HOST_IP']
    mqtt_id = machine_ip+''+local_ip
except:
    LOG.error('Error during the processing of the HOST IP')

topic = '$share/group1/0001/'

channel = None
q_name = None
rabbit_queue = None
MAX_MESSAGES = 6

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
            properties=pika.BasicProperties(delivery_mode = 2)
        )

        if(int(q_l) >= (MAX_MESSAGES-1)):
            client.unsubscribe(topic)
            while True:
                time.sleep(1)
                LOG.info('Waiting for publishing...')
                q_ll = rabbit_queue.method.message_count
                if(int(q_ll) <= (MAX_MESSAGES/2)):
                    client.subscribe(topic, qos = 2)
                    break
    except:
        LOG.error('Error during update RubbitMQ queue.')
        sys.exit()

time.sleep(20)

LOG.info('Starting connection with RubbitMQ server...')
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=machine_ip, port=5672))
    channel = connection.channel()
except:
    LOG.error('Connection error with RubbitMQ server.')
    sys.exit()

LOG.info('Starting connection with MQTT Broker...')
try:
    client = mqtt.Client(client_id = mqtt_id, clean_session = False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('InternalKalpaELB-c6dcbc9047674e10.elb.eu-west-1.amazonaws.com')
    client.loop_forever()
except:
    LOG.error('Connection error with MQTT Broker.')
    sys.exit()