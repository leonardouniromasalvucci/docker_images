import paho.mqtt.client as mqtt
import time, sys, os
from threading import Thread
import time, random, json, datetime, logging
from datetime import timezone
import argparse

parser = argparse.ArgumentParser(description='This is a script to simulate several IoT devices.')
parser.add_argument('-n','--devices_number', help='Number of devices',required=False)
parser.add_argument('-is','--interval_message_sent', help='Interval time of messages', required=False)
parser.add_argument('-ic','--interval_device_creation', help='Interval time of devices creation', required=False)
parser.add_argument('-qos','--qos', help='Define the quality of service', required=False)
parser.add_argument('-s','--enable_tls', help='Allow security communivcation through TLS', required=False)
args = parser.parse_args()

devices_number = None
interval_message_sent = None
interval_device_creation = None
enable_tls = None
qos = None

if(args.devices_number == None):
	devices_number = 1
else:
	devices_number = args.devices_number

if(args.interval_message_sent == None):
	interval_message_sent = 5
else:
	interval_message_sent = args.interval_message_sent

if(args.interval_device_creation == None):
	interval_device_creation = 5
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
	if rc==0:
		print("Connected with returned code = ", rc)
	else:
		print("Bad connection with returned code = ", rc)
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
		print ("Device " + str(self.id) + " is running...")
		broker = "InternetKalpaELB-5c0c715d50ed9d71.elb.eu-west-1.amazonaws.com"
		
		client = mqtt.Client(client_id = str(self.id), protocol = 5)
		client.on_connect = on_connect
		client.enable_logger(LOG)
		client.username_pw_set("dev-01", "dev-01234")
		client.loop_start()

		r = client.connect(host = broker, port = 1883, keepalive = 120, clean_start = True, properties = None)
		print("Connected to broker ", broker, " with code ", r)

		while True:
			try:
				dt = datetime.datetime.now() 
				utc_time = dt.replace(tzinfo = timezone.utc)
				m = json.dumps(Message(utc_time.timestamp(), "lightness", str(round(random.uniform(0.5, 1.9),3))).__dict__)
				client.publish("/7/0/", m, int(qos))
				print("Device "+ str(self.id) + " has published: " + m)
				time.sleep(int(interval_message_sent))
			except:
				print("ERR")
				time.sleep(int(interval_message_sent))

for devices_id in range(1, int(devices_number) + 1):
	try:
		new_device = Device(devices_id)
		new_device.daemon = True
		new_device.start()
		time.sleep(random.uniform(0, int(interval_device_creation)))
	except:
		print("Error during creation of device " + str(devices_id))
		sys.exit(1)

while True:
	try:
		pass
	except KeyboardInterrupt:
		sys.exit()