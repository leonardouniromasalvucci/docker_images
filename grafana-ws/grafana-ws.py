#!/usr/bin/python3

import griddb_python as griddb
import flask, logging, os, sys, datetime, json, time, socket, subprocess, threading
from flask import request, jsonify

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

gridstore = None
col = None
factory = None
update = True

def append_to_list(list, label, value):
    if (not any(label in d['target'] for d in list)):
        list.append({"target": label, "datapoints": [value]})
    else:
        for i in list:
            if(i['target'] == label):
                i['datapoints'].append(value)
    return list

def to_timestamp(date):
    time_tuple = date.timetuple()
    timestamp = time.mktime(time_tuple)
    return timestamp

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "<h1>GridDB Client for Grafana</h1><p>GridDB client to extract data from cluster.</p>"

@app.route('/<homeid>')
def grafana_connection(homeid):
        return 'Success to connect to ENDPOINT '+ str(homeid) +'!', 200

@app.route('/<homeid>/search',methods = ['POST', 'GET'])
def grafana_search(homeid):
        return jsonify([]), 200

@app.route('/<homeid>/query',methods = ['POST', 'GET'])
def grafana_query(homeid):
        try:

                factory = griddb.StoreFactory.get_instance()
                gridstore = factory.get_store(
                        notification_member="10.0.0.28:10001,10.0.0.37:10001,10.0.0.172:10001",
                        cluster_name="defaultCluster",
                        username="admin",
                        password="admin"
                )

                LOG.info("[MultiGet S] HOME ID = " + homeid)

                results = []

                listCon = []
                listQuery = []
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
                                results = append_to_list(results, row[1], [row[2], to_timestamp(row[0])])
                                LOG.info(row)

                LOG.info("[MultiGet E]")

        except griddb.GSException as e:
                for i in range(e.get_error_stack_size()):
                        LOG.err("[", i, "]")
                        LOG.err(e.get_error_code(i))
                        LOG.err(e.get_message(i))

        return jsonify(results), 200

app.run(host='0.0.0.0', port=8080)