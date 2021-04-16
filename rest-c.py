import requests

#url = 'https://RESTalb-1562068755.eu-west-1.elb.amazonaws.com:8080/6/query'#data/6/all'
url = 'http://localhost/data/6'#data/6/all'
myobj = '{"app":"dashboard","requestId":"Q103","timezone":"browser","panelId":23763571993,"dashboardId":1,"range":{"from":"2021-04-13T16:32:15.000Z","to":"2021-04-13T16:32:15.000Z","raw":{"from":"2021-04-13T16:32:15.000Z","to":"2021-04-13T16:32:15.000Z"}},"timeInfo":"","interval":"10ms","intervalMs":10,"targets":[{"data":"","refId":"A","target":"","type":"timeseries","datasource":"JSON"}],"maxDataPoints":1104,"scopedVars":{"__interval":{"text":"10ms","value":"10ms"},"__interval_ms":{"text":"10","value":10}},"startTime":1618508524965,"rangeRaw":{"from":"2021-04-13T16:32:15.000Z","to":"2021-04-13T16:32:15.000Z"},"adhocFilters":[]}'
#x = requests.get(url, data = myobj, headers={"content-type":"text"})

#x = requests.get(url, headers={"X-User":"grafana-test", "X-Password":"grafana-1234"}, verify=False)

x = requests.post(url, data = myobj, headers={"X-User":"grafana-test", "X-Password":"grafana-1234"}, verify=False)

print(x.text)