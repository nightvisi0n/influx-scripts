#!/usr/bin/env python3

import matplotlib.image as img
from influxdb import InfluxDBClient
import time

points = {}
influxclient = InfluxDBClient('hostname', 8086, 'username', 'password', 'database')

image = img.imread('icmp.png')

while True:
    for c in range(image.shape[1]):
        json = {}
        json['000'] = 0
        for r in range(image.shape[0]):
            json[str(image.shape[0]-r).zfill(3)] = 1-int(image[r,c])
        json['101'] = 0
        influxclient.write_points(
            [{
                "measurement": "img_symbols",
                "time": int(time.time()*10**9),
                "fields": json
            }]
        )
        time.sleep(10)
    time.sleep(60)
