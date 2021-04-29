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


        html = '<html> <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> <title>Monitoring</title> <meta name="viewport" content="width=device-width, initial-scale=1">  <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"> </head>'
        html += '<body><div class="col-md-6 col-md-offset-3"> <h3>Message monitoring</h3> <table class="table table-striped table-bordered" style="margin-top:40px;">' #<table align="center" style="margin-top:50px;width:20%;border-collapse: collapse;border: 1px solid black;">
        html += '<tr><th style="text-align:center;">Published</th><th style="text-align:center;">Stored</th><th style="text-align:center;color:#d9534f">Lost</th></tr>'
        html += '<tr style="border: 1px solid black;"><td style="text-align:center;margin-top:10px;">'+str(messages_sent_by_clients)+'</td><td style="text-align:center;margin-top:10px;">'+str(len(results))+'</td><td style="text-align:center;margin-top:10px;color:#d9534f"">'+str(messages_sent_by_clients-len(results))+'</td></tr>'
        html += '</table>'
        html += '</body></html>'
        return html, 200


@app.route('/increment', methods=['GET'])
def increment():
        global messages_sent_by_clients
        messages_sent_by_clients = messages_sent_by_clients+1
        return 'Success!', 200

@app.route('/', methods=['GET'])
def home():
    return "<h1>GridDB Client for Grafana</h1><p>GridDB client to extract data from cluster.</p>", 200


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
                                if time == "hour":
                                        query = container.query("select * where timestamp > TIMESTAMPADD(HOUR, NOW(), -1)")
                                elif(time == "day"):
                                        query = container.query("select * where timestamp > TIMESTAMPADD(HOUR, NOW(), -24)")
                                else:
                                        query = container.query("select *")

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

@app.route('/data/json/<homeid>/<time>')
def get_data_json(homeid, time):
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
                                        if time == "hour":
                                                query = container.query("select * where timestamp > TIMESTAMPADD(HOUR, NOW(), -1)")
                                        elif(time == "day"):
                                                query = container.query("select * where timestamp > TIMESTAMPADD(HOUR, NOW(), -24)")
                                        else:
                                                query = container.query("select *")
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

                r_body = jsonify(results)
                r_code = 200
        else:
                r_body = "Unauthorized request"
                r_code = 400
        
        return r_body, r_code


app.run(host='0.0.0.0', port=80)