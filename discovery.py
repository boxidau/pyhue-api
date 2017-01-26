#! /usr/bin/env python
# -*- coding: utf-8 -*-
#######################

import socket
import sys
import time
import threading
import json

with open('config.json') as config_fp:
  config_data = json.load(config_fp)

HOST_IP = config_data['host']
SERVER_PORT = config_data['port']
BCAST_IP = "239.255.255.250"
UPNP_PORT = 1900
BROADCAST_INTERVAL = 10  # Seconds between upnp broadcast
M_SEARCH_REQ_MATCH = "M-SEARCH"
UUID = config_data['uuid']

broadcast_packet = """NOTIFY * HTTP/1.1
HOST: %(broadcast_ip)s:%(upnp_port)s
CACHE-CONTROL: max-age=100
LOCATION: http://%(server_ip)s:%(server_port)s/description.xml
SERVER: FreeRTOS/7.4.2, UPnP/1.0, IpBridge/1.7.0
NTS: ssdp:alive
NT: uuid:%(uuid)s
USN: uuid:%(uuid)s

"""

response_packet = """HTTP/1.1 200 OK
CACHE-CONTROL: max-age=100
EXT:
LOCATION: http://{server_ip}:{server_port}/description.xml
SERVER: FreeRTOS/7.4.2, UPnP/1.0, IpBridge/1.7.0
ST: urn:schemas-upnp-org:device:basic:1
USN: uuid:{uuid}s

"""

def respond(addr):
  output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  response_data = {"server_ip": HOST_IP,
                   "server_port": SERVER_PORT, 
                   "uuid": UUID}

  output_packet = response_packet.format(**response_data)
  print(repr(output_packet))
  output_socket.sendto(output_packet.encode(), addr)
  output_socket.close()

def run():
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(('', UPNP_PORT))
    sock.setsockopt(socket.IPPROTO_IP,
                    socket.IP_ADD_MEMBERSHIP,
                    socket.inet_aton(BCAST_IP) + socket.inet_aton(HOST_IP))
    sock.settimeout(10)

    while True:
      try:
        print('Waiting for packet')
        data, addr = sock.recvfrom(1024)
        print(data.decode('utf8'))
        if M_SEARCH_REQ_MATCH in data.decode('utf8'):
          respond(addr)

      except socket.error:
        print(str(sys.exc_info()[0]))

if __name__ == '__main__':
  run()
