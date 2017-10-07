import socket
import cv2
import numpy
from threading import Thread
import time
import sys
import re
import threading
import signal
from datetime import datetime, timedelta



IP = '127.0.0.1'
# UDP_IP = "127.0.0.1"
UDP_PORT = 10021
TCP_PORT = 2100
MESSAGE = "Hello, World!"
REFRESH_MESSAGE = "Refresh"

class Killing:
    def __init__(self):
        self.kill = False

    def set_kill():
        self.kill = True

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
    for k in args[1:]:
        if ip_address_regex.match(k):
            IP = k
        elif k.lower() == 'udp':
            protocolUDP = True
    kil = Killing()

    if protocolUDP:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(MESSAGE, (IP, UDP_PORT))
        udp_socket.settimeout(2)
        mySubscriber = Subscriber(udp_socket)
        mySubscriber.start()
        def finish_it_up(a,b):
            mySubscriber.stop()
            udp_socket.close()
            mySubscriber.join()
            kil.kill = True
        signal.signal(signal.SIGINT, finish_it_up)
        last_sequence_number = 0
        while True:
            if kil.kill:
                break
            try:
                data, address = udp_socket.recvfrom(65536)
                current_sequence_number = int(data[0:6])
                # Dump slower / past packets
                if (last_sequence_number < current_sequence_number):
                    last_sequence_number = current_sequence_number
                    frame_string = data[6:]
                    frame_matrix = numpy.fromstring(frame_string, dtype='uint8')
                    decoded_image = cv2.imdecode(frame_matrix, 1)
                    cv2.imshow('CLIENTE UDP', decoded_image)
                else:
                    print 'Frame skipped: %s' % current_sequence_number
                # Quit command capture
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    finish_it_up(None, None)
                    break
            except socket.timeout:
                if last_sequence_number == 0:
                    print >> sys.stderr, 'No se ha podido conectar al servidor, reintentando...'
                else:
                    print >> sys.stderr, 'Conexion perdida, reintentando...'
                try:
                    udp_socket.sendto(MESSAGE, (IP, UDP_PORT))
                    data, address = udp_socket.recvfrom(65536)
                    last_sequence_number = 1
                except socket.timeout:
                    if last_sequence_number == 0:
                        print >> sys.stderr, 'Reintento fallido, finalizando programa'
                    else:
                        print >> sys.stderr, 'Conexion perdida, finalizando programa'
                    finish_it_up(None, None)
                    break

    else:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((IP, TCP_PORT))
        bufferstring = ''
        def finish_it_up(a,b):
            kil.kill = True
            tcp_socket.shutdown(socket.SHUT_WR)
            tcp_socket.settimeout(1)
            ending_time = datetime.now()
            try:
                data = ''
                while (datetime.now() - ending_time < timedelta(seconds = 5)):
                    data = tcp_socket.recv(4096)
            except:
                None
            tcp_socket.close()
        signal.signal(signal.SIGINT, finish_it_up)
        while True:
            if kil.kill:
                break
            data = tcp_socket.recv(4096)
            if data == '':
                tcp_socket.close()
                break
            bufferstring = bufferstring + data
            pieces = re.split('inicio', bufferstring)
            if len(pieces) > 1:
                for frame in pieces[:-1]:
                    cleanframe = re.sub('sustituyendo_palabra','inicio', frame)
                    data = numpy.fromstring(cleanframe, dtype='uint8')
                    decimg=cv2.imdecode(data,1)
                    cv2.imshow('CLIENTE TCP',decimg)
            bufferstring = pieces[-1]
            if cv2.waitKey(1) & 0xFF == ord('q'):
                finish_it_up(None, None)
                break
