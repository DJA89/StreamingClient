import socket
import cv2
import numpy

UDP_IP = "127.0.0.1"
UDP_PORT = 10021
MESSAGE = "Hello, World!"


def client():
    udp_socket = socket.socket(socket.AF_INET,
    socket.SOCK_DGRAM)
    udp_socket.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    while True:
        data, address = udp_socket.recvfrom(65536)
        data = numpy.fromstring(data, dtype='uint8')
        decimg = cv2.imdecode(data, 1)
        cv2.imshow('frame',decimg)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    while True:
        None
client()
