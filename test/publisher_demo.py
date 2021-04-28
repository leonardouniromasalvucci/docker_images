import paho.mqtt.client as mqtt
import time, sys, os
from threading import Thread
import time, random, json, datetime, logging
from datetime import timezone
import keyboard
import ssl
import argparse, requests

parser = argparse.ArgumentParser(description='This is a script to simulate several IoT devices.')
parser.add_argument('-n','--devices_number', help='Number of devices',required=False)
parser.add_argument('-m','--num_messages', help='Number of messages for each client', required=False)
parser.add_argument('-is','--interval_message_sent', help='Interval time of messages', required=False)
parser.add_argument('-ic','--interval_device_creation', help='Interval time of devices creation', required=False)
parser.add_argument('-qos','--qos', help='Define the quality of service', required=False)
parser.add_argument('-s','--enable_tls', help='Allow security communivcation through TLS', required=False)
args = parser.parse_args()

sensor_type = ['temperature', 'humidity', 'energy']
# https://aws.amazon.com/it/blogs/iot/how-to-implement-mqtt-with-tls-client-authentication-on-port-443-from-client-devices-python/

devices_number = None
interval_message_sent = None
interval_device_creation = None
enable_tls = None
qos = None

if(args.devices_number == None):
	devices_number = 3
else:
	devices_number = args.devices_number

if(args.num_messages == None):
	num_messages = 100
else:
	num_messages = args.num_messages

if(args.interval_message_sent == None):
	interval_message_sent = 10
else:
	interval_message_sent = args.interval_message_sent

if(args.interval_device_creation == None):
	interval_device_creation = 1
else:
	interval_device_creation = args.interval_device_creation

if(args.qos == None):
	qos = 2
else:
	qos = args.qos

if(args.enable_tls == None):
	enable_tls = "y"
else:
	enable_tls = args.enable_tls


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc, properties=None):
	return rc


class Message:
  def __init__(self, timestamp, label, value):
	  self.timestamp = timestamp
	  self.label = label
	  self.value = value
	
class Device(Thread):

	def __init__(self, id):
		Thread.__init__(self)
		self.id = id
	
	def run(self):
		print ("Device " + str(self.id) + " is running.")
		broker = "InternetKalpaELB-5c0c715d50ed9d71.elb.eu-west-1.amazonaws.com"
		client = mqtt.Client(client_id = str(self.id), protocol = 5)
		client.on_connect = on_connect
		client.username_pw_set("dev-01", "dev-01234")
		client.loop_start()
		client.connect(host = broker, port = 1883, keepalive = 120, clean_start = True, properties = None)

		i=0
		while True:
			while(i<num_messages):
				try:
					dt = datetime.datetime.now() 
					utc_time = dt.replace(tzinfo = timezone.utc)
					m = json.dumps(Message(utc_time.timestamp(), sensor_type[self.id], str(round(random.uniform(0.5, 1.9),3))).__dict__)
					client.publish("/70/"+str(self.id)+"/", m, int(qos))
					print("Device "+ str(self.id) + " has published: " + m)
					time.sleep(float(interval_message_sent))
					i=i+1
				except:
					print("ERR")
					time.sleep(float(interval_message_sent))

			print("Device "+ str(self.id) + " has FINISHED.")
			break

for devices_id in range(0, int(devices_number)):
	try:
		new_device = Device(devices_id)
		new_device.daemon = True
		new_device.start()
		time.sleep(random.uniform(0, float(interval_device_creation)))
	except:
		print("Error during creation of device " + str(devices_id))
		sys.exit(1)

while True:
	try:
		pass
	except KeyboardInterrupt:
		sys.exit()