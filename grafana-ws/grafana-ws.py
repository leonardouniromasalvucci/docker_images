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

app = flask.Flask(__name__)
app.config["DEBUG"] = True

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
        LOG.info(request.headers)
        data = request.get_data().decode("utf-8")
        LOG.info(data)
        #head_usr = request.headers['X-User']
        #LOG.info(head_usr)
        #head_psw = request.headers['X-Password']
        #LOG.info(head_psw)

        r_body = None
        r_code = None

        if(request.headers['X-User'] == "grafana-test" and request.headers['X-Password'] == "grafana-1234"):
                #data = request.get_data().decode("utf-8")
                #LOG.info(data)
                y = json.loads(data)
                LOG.info(y['range']['from'])
                LOG.info(y['range']['to'])
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
                                        query = container.query("select * where timestamp > TIMESTAMP('" + y['range']['from'] + "') AND timestamp < TIMESTAMP('" + y['range']['to'] + "')")
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
                                        results = append_to_list(results, row[1], [float(row[2]), to_timestamp(row[0])])
                                        LOG.info(row)

                        LOG.info("[MultiGet E]")

                except griddb.GSException as e:
                        LOG.info(e.get_message(i))

                LOG.info(results)
                r_body = jsonify(results)
                LOG.info(r_body)
                r_code = 200
        else:
                r_body = "Unauthorized request"
                r_code = 401
                
        return r_body, r_code

app.run(host='0.0.0.0', port=8081)