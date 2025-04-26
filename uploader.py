#!/usr/bin/env python3

import meshtastic
import meshtastic.tcp_interface
from pubsub import pub
import time
import datetime
import math
import json
import traceback



# Received: {'from': 530607104, 'to': 131047185, 'decoded': {'portnum': 'TEXT_MESSAGE_APP', 'payload': b'G', 'bitfield': 1, 'text': 'G'}, 'id': 103172025, 'rxTime': 1745376860, 'rxSnr': 7.0, 'hopLimit': 7, 'wantAck': True, 'rxRssi': -14, 'hopStart': 7, 'publicKey': 'Jn89K4tEsX2fKYy+NUu3J8EJ/gjXjxP1SQCHm3A8Wms=', 'pkiEncrypted': True, 'raw': from: 530607104, to: 131047185, [...], 'fromId': '!1fa06c00', 'toId': '!07cf9f11'}

position = None

def onReceive(packet, interface):
    global position
    print(f"Received: {packet}")
    if packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
        payload = packet['decoded']['payload'].decode('utf-8')
        if payload[0:3] == "mtf1:"
    except Exception as e:
        print('Masking exception:')
        traceback.print_exc()

pub.subscribe(onReceive, "meshtastic.receive")
interface = meshtastic.tcp_interface.TCPInterface(hostname='172.16.17.103')

while True:
    my = interface.getMyNodeInfo()
    pos = my['position']
    if {'altitude', 'latitude', 'longitude'}.issubset(pos):
        position = {
            'alt': my['position']['altitude'],
            'lat': my['position']['latitude'],
            'lon': my['position']['longitude'],
        }
        print(f"Have local node GPS position: {position['alt']} {position['lat']} {position['lon']}")
    time.sleep(30)


interface.close()
