#!/usr/bin/env python3

import isc_dhcp_leases
from netaddr import IPNetwork, IPAddress
from influxdb import InfluxDBClient
import time

leases = isc_dhcp_leases.IscDhcpLeases('/var/lib/dhcp/dhcpd.leases', False).get_current()
networks = {
        IPNetwork('94.45.228.0/22'): "wired",
        IPNetwork('94.45.232.0/23'): "2.4GHz_auth",
        IPNetwork('94.45.234.0/23'): "5GHz_auth",
        IPNetwork('94.45.236.0/22'): "wifi_open",
}

json = []

for cidr, name in networks.items():
    lsum = 0
    for lease in leases.values():
        if IPAddress(lease.ip) in cidr and lease.valid and lease.active:
            lsum += 1
    print(name + ": " + str(lsum))
    json.append(
        {
	    "measurement": "dhcp_leases",
            "tags": {
                "host": "dns",
                "network": name
            },
            "time": int(time.time()*10**9),
            "fields": {
                "active": lsum
            }
        }
    )

print(json)

client = InfluxDBClient('hostname', 8086, 'user', 'password', 'database')
client.write_points(json)
