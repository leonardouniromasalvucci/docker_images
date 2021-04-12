#!/usr/bin/python3

import griddb_python as griddb
import flask, logging, os, sys, datetime, json, time, socket, subprocess, threading
from datetime import datetime

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

col = None
factory = None
update = True


app = flask.Flask(__name__)
app.config["DEBUG"] = True

def connect_to_griddb():
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


@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

connect_to_griddb()
app.run()