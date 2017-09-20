import socket
import cv2
import numpy
from threading import Thread
import time
import sys
import re


UDP_IP = "127.0.0.1"
# UDP_IP = "127.0.0.1"
UDP_PORT = 10021
MESSAGE = "Hello, World!"
REFRESH_MESSAGE = "Refresh"

class Subscriber(Thread):
    def __init__(self, udp_socket):
        Thread.__init__(self)
        self.udp_socket = udp_socket

    def run(self):
        while True:
            time.sleep(30)
            udp_socket.sendto(REFRESH_MESSAGE, (UDP_IP, UDP_PORT))

if __name__ == '__main__':
    args = sys.argv
    ip_address_regex = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\Z')
    try:
        if ip_address_regex.match(args[1]):
            UDP_IP = args[1]
    except IndexError:
        None
    udp_socket = socket.socket(socket.AF_INET,
    socket.SOCK_DGRAM)
    udp_socket.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    mySubscriber = Subscriber(udp_socket)
    mySubscriber.daemon = True
    mySubscriber.start()
    while True:
        data, address = udp_socket.recvfrom(65536)
        data = numpy.fromstring(data, dtype='uint8')
        decimg = cv2.imdecode(data, 1)
        cv2.imshow('frame',decimg)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
