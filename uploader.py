#!/usr/bin/env python3

import meshtastic
import meshtastic.tcp_interface, meshtastic.ble_interface, meshtastic.serial_interface
from pubsub import pub
import time
import datetime
import json
import traceback
import sondehub

from sondehub.amateur import Uploader

# Received: {'from': 530607104, 'to': 131047185, 'decoded': {'portnum': 'TEXT_MESSAGE_APP', 'payload': b'G', 'bitfield': 1, 'text': 'G'}, 'id': 103172025, 'rxTime': 1745376860, 'rxSnr': 7.0, 'hopLimit': 7, 'wantAck': True, 'rxRssi': -14, 'hopStart': 7, 'publicKey': 'Jn89K4tEsX2fKYy+NUu3J8EJ/gjXjxP1SQCHm3A8Wms=', 'pkiEncrypted': True, 'raw': from: 530607104, to: 131047185, [...], 'fromId': '!1fa06c00', 'toId': '!07cf9f11'}

position = None
balloon_position = None

def onReceive(packet, interface):
    global position
    global balloon_position
    #print(packet)
    try:
        if packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            payload = packet['decoded']['payload'].decode('utf-8')
            print(f"text message from {packet['fromId']} to {packet['toId']}: {payload}")
            if payload[0:5] == "mtf1:":
                print("got mtf1 packet!")
                # mtf:{"chUtil": 4.68, "airUtilTx": 4.68, "uptime": 6625, "alt": 255, "lat": 41.8808, "lon": -88.0771}
                telem = json.loads(payload[5:])
                snr = rssi = None
                try:
                    snr = packet['rx_snr']
                    rssi = packet['rx_rssi']
                except KeyError as e:
                    print("no snr/rssi in packet...weird.")
                if not {'lat', 'lon', 'alt', 'gpstime'}.issubset(telem):
                    print("Balloon doesn't have a GPS fix - not good.")
                    return
                uploader.add_telemetry(
                    "KD9PRC-MT", # TODO: derive payload name from the node, not just hardcode to what i want...but node name comes from nodeInfo...which we might not have yet...i am tired and lazy...and wondering if there's a limit to how long i can keep writing this comment...
                    datetime.datetime.utcfromtimestamp(telem['gpstime']),
                    telem['lat'],
                    telem['lon'],
                    telem['alt'],
                    modulation='Meshtastic Rx',
                    uploader_callsign=station_callsign,
                    snr=snr,
                    rssi=rssi,
                    extra_fields={
                        'chUtil': telem['chUtil'],
                        'airUtilTx': telem['airUtilTx'],
                        'uptime': telem['uptime'],
                    }
                    )
                if have_local_gps:
                    uploader.upload_station_position(
                        station_callsign,
                        [telem['lat'], telem['lon'], telem['alt']],
                        )
                print(f"uploaded packet from balloon to sondehub! {telem['lat']} {telem['lon']} {telem['alt']}")

    except Exception as e:
        print('Masking exception:')
        traceback.print_exc()

pub.subscribe(onReceive, "meshtastic.receive")
################ You will need to customize this! ########################
interface = meshtastic.tcp_interface.TCPInterface(hostname='172.16.17.103')
#interface = meshtastic.ble_interface.BLEInterface('Redd_db3d')
#interface = meshtastic.serial_interface.SerialInterface('/dev/ttyACM0')
################ ok that's all :) ########################################
print("Opening connection to Sondehub...", end='')
my = interface.getMyNodeInfo()
station_callsign=my['user']['id']
uploader = Uploader(station_callsign, software_name="KD9PRC Mestastic local uploader", software_version="0.0.1")
print("Done. Check it out: https://amateur.sondehub.org/")

have_local_gps = False
while True:
    my = interface.getMyNodeInfo()
    if my is not None and 'position' in my:
        pos = my['position']
        if {'altitude', 'latitude', 'longitude'}.issubset(pos):
            position = {
                'alt': my['position']['altitude'],
                'lat': my['position']['latitude'],
                'lon': my['position']['longitude'],
            }
            print(f"Have local node GPS position: {position['alt']} {position['lat']} {position['lon']}")
        have_local_gps = True
        uploader.upload_station_position(
            station_callsign,
            [position['lat'], position['lon'], position['alt']],
            )
    else:
        have_local_gps = False
    time.sleep(30)


interface.close()
