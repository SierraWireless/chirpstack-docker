#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from chirpstack_api import integration
from google.protobuf.json_format import Parse

import requests
import json
from time import time

# AV system REST password
password="w$7X872#LDpqTN"

# Value used for the conversion of the position from DMS to decimal
MaxNorthPosition = 8388607 # 2^23 - 1
MaxSouthPosition = 8388608 # -2^23
MaxEastPosition = 8388607 # 2^23 - 1
MaxWestPosition = 8388608 # -2^23

class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        query_args = parse_qs(urlparse(self.path).query)

        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)

        if query_args["event"][0] == "up":
            self.up(body)

        elif query_args["event"][0] == "join":
            self.join(body)

        else:
            print("handler for event %s is not implemented" % query_args["event"][0])

    def up(self, body):
        up = self.unmarshal(body, integration.UplinkEvent())
        rssi = up.rx_info[0].rssi
        fsn = up.device_info.dev_eui.upper()
        data = up.data.hex().upper() # 830C3E3D05017805

        # Keep only data for AV (FPort: 31)
        if up.f_port != 31:
            return

        print("Uplink received from: %s with rssi: %s payload: %s" % (fsn, rssi, data))

        # Decode Latitude from Data Payload
        latitude = int(data[0:2], 16) + (int(data[2:4], 16) << 8) + (int(data[4:6], 16) << 16)

        # We want a signed int
        if int(data[4:6], 16) & 0x80:
            latitude = -((latitude - 1) ^ 0xffffff)

        if latitude < 0:
            # Negative => South latitude
            latitude = latitude * 90 / MaxSouthPosition
        else:
            # Positive => North latitude
            latitude = latitude * 90 / MaxNorthPosition

        print(latitude)

        # Decode Longitude from Data Payload
        longitude = int(data[6:8], 16) + (int(data[8:10], 16) << 8) + (int(data[10:12], 16) << 16)

        # We want a signed int
        if int(data[10:12], 16) & 0x80:
            longitude = -((longitude - 1) ^ 0xffffff)

        if longitude < 0:
            # Negative => West
            longitude = longitude * 180 / MaxWestPosition
        else:
            # Positive => East
            longitude = longitude * 180 / MaxEastPosition

        print(longitude)

        # Push to AV
        timestamp = int( time() * 1000)

        data = [
            {
                "tracker.location.type" : [
                    { "value" : "hardcoded", "timestamp" : timestamp}
                ],
                "_LONGITUDE" : [
                    { "value" : longitude, "timestamp" : timestamp}
                ],
                "_LATITUDE" : [
                    { "value" : latitude, "timestamp" : timestamp}
                ],
                "_OPERATOR" : [
                    { "value" : "Chirpstack", "timestamp" : timestamp}
                ],
                "_RSSI" : [
                    { "value" : rssi, "timestamp" : timestamp }
                ]
            }
        ]

        # Using Basic Authentication
        url = "https://eu.airvantage.net/device/messages"
        print("Sending to {}.".format(url))
        response = requests.post(
            url,
            auth=(fsn, password),
            data=json.dumps(data),
            headers={'Content-type': 'application/json'}
        )
        print("Response: {}. Content: {}".format(response.status_code, response.text))

    def join(self, body):
        join = self.unmarshal(body, integration.JoinEvent())
        print("Device: %s joined with DevAddr: %s" % (join.device_info.dev_eui, join.dev_addr))

    def unmarshal(self, body, pl):
        return Parse(body, pl)

httpd = HTTPServer(('0.0.0.0', 8100), Handler)

print("HTTP server waiting on port 8100")
httpd.serve_forever()
