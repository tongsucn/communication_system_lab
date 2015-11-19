#!/usr/bin/env python3
# Communication Systems Lab
# Assignment 3
# Task 3.2
# Author: Tong, Michael
# ##############################
# Description:
# Test script for Sensor Network Server
#

import socket
import struct
import time

class VirtualClient(object):
    """
    Simulating Clients.
    """

    def __init__(self, name, local_port):
        """
        Initializing.
        """

        # Data type
        # Registering
        self.TYPE_REG = 1
        self.data_reg = struct.pack('BB%ds' % len(name), self.TYPE_REG,
                                    len(name), name.encode())

        # Unregistering
        self.TYPE_UNREG = 2
        self.data_unreg = struct.pack('B', self.TYPE_UNREG)

        # Keep alive request
        self.TYPE_KEP = 3
        self.data_kep = struct.pack('B', self.TYPE_KEP)

        # Event request
        self.TYPE_EVE = 4
        self.data_eve = None

        # Shake broadcasting
        self.TYPE_SHK = 5

        # Server information
        self.tar_addr = '127.0.0.1'
        self.tar_port = 8123
        self.tar_pair = (self.tar_addr, self.tar_port)

        # Local information
        self.local_addr = '127.0.0.1'
        self.local_port = local_port
        self.local_pair = (self.local_addr, self.local_port)

        # Setting up
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.local_pair)


    def start(self):
        """
        Start client.
        """

        self.reg()
        data, ad = self.sock.recvfrom(256)
        print(data)


    def event(self, timestamp):
        """
        Sending shake event.
        """

        self.data_eve = struct.pack('!BQ', self.TYPE_EVE, timestamp)
        return self.sock.sendto(self.data_eve, self.tar_pair)


    def reg(self):
        """
        Sending registering request.
        """

        return self.sock.sendto(self.data_reg, self.tar_pair)


    def unreg(self):
        """
        Sending unregistering request.
        """

        return self.sock.sendto(self.data_unreg, self.tar_pair)


    def keepalive(self):
        """
        Sending unregistering request.
        """

        return self.sock.sendto(self.data_kep, self.tar_pair)


if __name__ == '__main__':
    client_lst = []

    for i in range(10):
        client_lst.append(VirtualClient('Client_%d' % i, 23333 + i))

    for client in client_lst:
        client.reg()

    client_lst[0].event(int(time.time()))
