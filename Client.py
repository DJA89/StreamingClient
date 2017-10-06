import socket
import cv2
import numpy
from threading import Thread
import time
import sys
import re
import threading
import signal



IP = '127.0.0.1'
# UDP_IP = "127.0.0.1"
UDP_PORT = 10021
TCP_PORT = 2100
MESSAGE = "Hello, World!"
REFRESH_MESSAGE = "Refresh"

class Subscriber(Thread):
    def __init__(self, udp_socket):
        Thread.__init__(self)
        self.udp_socket = udp_socket
        self._stop_event = threading.Event()

    def run(self):
        tiempo = 0
        while True:
            time.sleep(1)
            tiempo = tiempo + 1
            if self._stop_event.is_set():
                self.udp_socket.close()
                break
            elif tiempo == 30:
                tiempo = 0
                udp_socket.sendto(REFRESH_MESSAGE, (IP, UDP_PORT))

    def stop(self):
        self._stop_event.set()

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
        mySubscriber.start()
        def finish_it_up(a,b):
            mySubscriber.stop()
            udp_socket.close()
            mySubscriber.join()
        signal.signal(signal.SIGINT, finish_it_up)
        last_stamp = None
        while True:
            data, address = udp_socket.recvfrom(65536)
            frame_stamp = int(data[0:13])
            # Dump slower / past packets
            if (not last_stamp or (last_stamp < frame_stamp)):
                last_stamp = frame_stamp
                frame_string = data[13:]
                frame_matrix = numpy.fromstring(frame_string, dtype='uint8')
                decoded_image = cv2.imdecode(frame_matrix, 1)
                cv2.imshow('CLIENTE UDP', decoded_image)
            elif (last_stamp):
                print 'Frame skipped: %s' % frame_stamp
            # Quit command capture
            if cv2.waitKey(1) & 0xFF == ord('q'):
                finish_it_up(None, None)
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
                tcp_socket.shutdown(socket.SHUT_RDWR)
                tcp_socket.close()
                break
