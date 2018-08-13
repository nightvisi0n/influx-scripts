#!/usr/bin/env python3

import requests
import pprint
from influxdb import InfluxDBClient
import time
import html

baseurl = "https://ap-controller.wiese.icmp.camp/"
logindata = {"name": "root", "password": "changeme"}
mjson = []

session = requests.Session()

urls = {
    "login": baseurl + "login",
    "globalStat": baseurl + "monitor/getGlobalStat?token={token}",
    "ssidStats": baseurl + "monitor/ssidStats?token={token}",
    "allAps": baseurl + "monitor/allAps?token={token}"
}

def login():
    token = session.post(url=urls['login'], data=logindata).json()['value']
    print("Login successfull.")
    print("Got token: " + token)
    return token

def get_globalStat(token):
    rjson = session.post(url=urls['globalStat'].format(token=token)).json()
    return (
        {
	    "measurement": "global_stats",
            "time": int(time.time()*10**9),
            "fields": rjson
        }
    )

def get_ssidStats(token):
    rjson = session.post(url=urls['ssidStats'].format(token=token)).json()
    ret = []
    for ssid_stat in rjson:
        ssid_name = ssid_stat['ssid']
        ssid_stat.pop('ssid')
        ret.append(
            {
	        "measurement": "ssid_stats",
                "tags": {
                    "ssid": ssid_name
                },
                "time": int(time.time()*10**9),
                "fields": ssid_stat
            }
        )
    return ret

def get_allAps(token):
    rjson = session.post(url=urls['allAps'].format(token=token)).json()
    ret = []
    for ap_stat in rjson['data']:
        if ap_stat['status'] == 0:
            continue
        ret.append(
            {
	        "measurement": "ap_general",
                "tags": {
                    "name": html.unescape(ap_stat['name']),
                    "ip": ap_stat['ip'],
                    "mac": ap_stat['mac'],
                    "model": ap_stat['model']
                },
                "time": int(time.time()*10**9),
                "fields": {
                    "clientNum": ap_stat['clientNum'],
                    "clientNum2g": ap_stat['clientNum2g'],
                    "clientNum5g": ap_stat['clientNum5g'],
                    "uptime": int(ap_stat['uptime'].split(' days ')[0]) * 86400 + int(ap_stat['uptime'].split(' days ')[1].split(':')[0]) * 3600 + int(ap_stat['uptime'].split(' days ')[1].split(':')[1]) * 60 + int(ap_stat['uptime'].split(' days ')[1].split(':')[2]),
                    "2g_channel": ap_stat['wp2g']['actualChannel'].split('/')[0].strip(),
                    "2g_maxTxRate": ap_stat['wp2g']['maxTxRate'],
                    "2g_txPower": ap_stat['wp2g']['txPower'],
                    "2g_rxBytes": ap_stat['sca']['radioTraffic']['rxBytes'],
                    "2g_rxErrors": ap_stat['sca']['radioTraffic']['rxErrors'],
                    "2g_txBytes": ap_stat['sca']['radioTraffic']['txBytes'],
                    "2g_txErrors": ap_stat['sca']['radioTraffic']['txErrors'],
                    "5g_channel": ap_stat['wp5g']['actualChannel'].split('/')[0].strip(),
                    "5g_maxTxRate": ap_stat['wp5g']['maxTxRate'],
                    "5g_txPower": ap_stat['wp5g']['txPower'],
                    "5g_rxBytes": ap_stat['sca']['radioTraffic5g']['rxBytes'],
                    "5g_rxErrors": ap_stat['sca']['radioTraffic5g']['rxErrors'],
                    "5g_txBytes": ap_stat['sca']['radioTraffic5g']['txBytes'],
                    "5g_txErrors": ap_stat['sca']['radioTraffic5g']['txErrors']
                }
            }
        )
    return ret

def clean(j):
    for d in j['data']:
        d.pop('adoptInfo', None)

token = login()
mjson.append(get_globalStat(token))
mjson += get_ssidStats(token)
mjson += get_allAps(token)

client = InfluxDBClient('hostname', 8086, 'username', 'password', 'database')
pprint.pprint(mjson)
client.write_points(mjson)
