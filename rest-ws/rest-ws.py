#!/usr/bin/python3

import griddb_python as griddb
import flask, logging, os, sys, datetime, json, time, socket, subprocess, threading
from datetime import datetime
from flask import request

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

gridstore = None
col = None
factory = None
update = True

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>GridDB Client</h1><p>GridDB client to extract data from cluster.</p>"

@app.route('/myEndpoint')
def grafana_connection():
        return 'Success!', 200

@app.route('/myEndpoint/search')
def grafana_search():
        return [], 200

@app.route('/myEndpoint/query')
def grafana_query():
        return [], 200

@app.route('/data/<homeid>')
def get_data(homeid):
        try:
                factory = griddb.StoreFactory.get_instance()
                gridstore = factory.get_store(
                        notification_member="10.0.0.28:10001,10.0.0.37:10001,10.0.0.172:10001",
                        cluster_name="defaultCluster",
                        username="admin",
                        password="admin"
                )

                LOG.info("[MultiGet S] HOME ID = " + homeid)

                listCon = []
                listQuery = []
                #NumContainer = 2
                '''for i in range(1, NumContainer+1):
                        container = gridstore.get_container("home-"+homeid+"_device-"+str(i))
                        if container == None:
                                LOG.info("container: None")
                        listCon.append(container)
                        query = container.query("select * where timestamp > TIMESTAMPADD(MINUTE, NOW(), -2)")
                        if query == None:
                                LOG.info("query: None")
                        listQuery.append(query)
                        LOG.info("home-"+homeid+"_device-" + str(i))
                gridstore.fetch_all(listQuery)'''

                i=0
                while True:
                        try:
                                container = gridstore.get_container("home-"+homeid+"_device-"+str(i))
                                if container == None:
                                        LOG.info("container: None")
                                listCon.append(container)
                                query = container.query("select * where timestamp > TIMESTAMPADD(MINUTE, NOW(), -30)")
                                if query == None:
                                        LOG.info("query: None")
                                listQuery.append(query)
                                LOG.info("home-"+homeid+"_device-" + str(i))
                                i=i+1
                        except:
                                break
                        
                gridstore.fetch_all(listQuery)
                for q in listQuery:
                        rs = q.get_row_set()
                        while rs.has_next():
                                row = rs.next()
                                LOG.info(row)

                LOG.info("[MultiGet E]")

        except griddb.GSException as e:
                for i in range(e.get_error_stack_size()):
                        LOG.err("[", i, "]")
                        LOG.err(e.get_error_code(i))
                        LOG.err(e.get_message(i))

        return 'Success!', 200

app.run(host='0.0.0.0', port=80)