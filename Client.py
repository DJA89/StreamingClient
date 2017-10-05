import socket
import cv2
import numpy
from threading import Thread
import time
import sys
import re


IP = "127.0.0.1"
# UDP_IP = "127.0.0.1"
UDP_PORT = 10021
TCP_PORT = 2100
MESSAGE = "Hello, World!"
REFRESH_MESSAGE = "Refresh"

class Subscriber(Thread):
    def __init__(self, udp_socket):
        Thread.__init__(self)
        self.udp_socket = udp_socket

    def run(self):
        while True:
            time.sleep(30)
            udp_socket.sendto(REFRESH_MESSAGE, (IP, UDP_PORT))

if __name__ == '__main__':
    args = sys.argv
    ip_address_regex = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\Z')
    protocolUDP = False
    for k in args[1:2]:
        if ip_address_regex.match(k):
            IP = k
        elif k.lower() == 'udp':
            protocolUDP = True

    if protocolUDP:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(MESSAGE, (IP, UDP_PORT))
        mySubscriber = Subscriber(udp_socket)
        mySubscriber.daemon = True
        mySubscriber.start()
        while True:
            data, address = udp_socket.recvfrom(65536)
            data = numpy.fromstring(data, dtype='uint8')
            decimg = cv2.imdecode(data, 1)
            cv2.imshow('CLIENTE UDP',decimg)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((IP, TCP_PORT))

        bufferstring = ''
        while True:
            bufferstring = bufferstring + tcp_socket.recv(4096)
            pieces = re.split('inicio', bufferstring)
            if len(pieces) > 1:
                for frame in pieces[:-1]:
                    cleanframe = re.sub('sustituyendo_palabra','inicio', frame)
                    data = numpy.fromstring(cleanframe, dtype='uint8')
                    decimg=cv2.imdecode(data,1)
                    cv2.imshow('CLIENTE TCP',decimg)
            bufferstring = pieces[-1]
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
