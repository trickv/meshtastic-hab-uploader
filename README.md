A little uploader for custom-defined packets downlinked over Meshtastic sent from https://github.com/trickv/meshtastic-hab-bot-v2

This connects to your Meshtastic node, listens for packets on channel index 1 "BalloonData" key vSHBJpTtJU3VvpQX3DYfAZUEfaHy4uYXVbHTVrx0ItA=
When you get packets from the balloon, they'll be little json docs which this parses and uploads to Sondehub: https://amateur.sondehub.org/

To get this running you'll need a Python 3 environment with the meshtastic and sondehub PyPi packages installed, like:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Once that's done, decide how to connect to your node. There's no CLI arguments in this quick little script yet, so edit the code where it says
```
interface = meshtastic.tcp_interface.TCPInterface(hostname='172.16.17.103')
```
If you're doing TCP, just edit the IP.  If you're doing Serial or BLE (both should work) uncomment the appropriate code example.

My T-Beam is flaky, so I run it in a wrapper script because it dies a lot.  My RAK node on BLE doesn't have this problem. YMMV - this is Meshtastic after all.  First some features.  Quality comes later.
