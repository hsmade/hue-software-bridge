#!/usr/bin/env python2.7

import socket
import argparse
from string import Template
from time import sleep

parser = argparse.ArgumentParser(description='uPnP sender')
parser.add_argument('--ip', dest='ip', action='store', required=True) 
parser.add_argument('--port', dest='port', action='store', required=True) 
parser.add_argument('--mac', dest='mac', action='store', required=True) 
args = parser.parse_args()
mac = args.mac

dest_ip = '239.255.255.250'
dest_port = 1900

delay = 1
broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

message = Template('''NOTIFY * HTTP/1.1\r
HOST: 239.255.255.250:1900\r
CACHE-CONTROL: max-age=100\r
LOCATION: http://$ip:$port/description.xml\r
SERVER: FreeRTOS/6.0.5, UPnP/1.0, IpBridge/0.1\r
NTS: ssdp:alive\r
NT: $nt\r
USN: $usn\r
\r
''')

message_values = [
    { 
        'nt': 'upnp:rootdevice', 
        'usn': 'uuid:2f402f80-da50-11e1-9b23-{mac}::upnp:rootdevice'.format(mac=mac),
    },
    { 
        'nt': 'uuid:2f402f80-da50-11e1-9b23-{mac}'.format(mac=mac), 
        'usn': 'uuid:2f402f80-da50-11e1-9b23-{mac}'.format(mac=mac),
    },
    { 
        'nt': 'urn:schemas-upnp-org:device:basic:1', 
        'usn': 'uuid:2f402f80-da50-11e1-9b23-{mac}'.format(mac=mac),
    },
]

while True:
    for msg in message_values:
        msg.update({'ip': args.ip, 'port': args.port})
        message_string = message.substitute(msg)
        print message_string
        broadcast.sendto(message_string, (dest_ip, dest_port))
    sleep(delay)
