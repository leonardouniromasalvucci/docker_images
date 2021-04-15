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

messages_sent_by_clients = 0

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

@app.route('/reset', methods=['GET'])
def reset():
        global messages_sent_by_clients
        messages_sent_by_clients = 0
        return 'Success!', 200

@app.route('/<homeid>/monitoring', methods=['GET'])
def monitoring(homeid):
        global messages_sent_by_clients

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
                                results.append(row)
                                LOG.info(row)

                LOG.info("[MultiGet E]")

        except griddb.GSException as e:
                for i in range(e.get_error_stack_size()):
                        LOG.err("[", i, "]")
                        LOG.err(e.get_error_code(i))
                        LOG.err(e.get_message(i))

                        
        html = '<table style="width:30%"><tr><th>Sent</th><th>Stored</th></tr>'
        html += '<tr><td>'+str(messages_sent_by_clients)+'</td><td>'+str(len(results))+'</td></tr>'
        html += '</table>'
        return html, 200


@app.route('/increment', methods=['GET'])
def increment():
        global messages_sent_by_clients
        messages_sent_by_clients = messages_sent_by_clients+1
        return 'Success!', 200

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
        data = request.get_data().decode("utf-8")
        LOG.info(data)
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


@app.route('/data/<homeid>/<time>')
def get_data(homeid, time):
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
                                query = None
                                if time == "all":
                                        query = container.query("select *")
                                else:
                                        query = container.query("select * where timestamp > TIMESTAMPADD(MINUTE, NOW(), -60)")
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
                                results.append(row)
                                LOG.info(row)

                LOG.info("[MultiGet E]")

        except griddb.GSException as e:
                for i in range(e.get_error_stack_size()):
                        LOG.err("[", i, "]")
                        LOG.err(e.get_error_code(i))
                        LOG.err(e.get_message(i))

        html = '<table style="width:30%"><tr><th>Timestamp</th><th>Label</th><th>Value</th></tr>'
        for i in results:
                html += '<tr>'
                for k in i:
                        html += '<td>'+ str(k) +'</td>'        
                html += '</tr>'
        html += '</table>'
        return html, 200

app.run(host='0.0.0.0', port=80)