#!/usr/bin/env python3
# Communication Systems Lab
# Assignment 3
# Task 3.2
# Author: Tong, Michael
# ##############################
# Description:
# Sensor Network Protocol
#

# Asynchronous IO support
import asyncio
import time
import struct

import logging


class SensorNetProtocol(asyncio.DatagramProtocol):
    """
    Sensor Network Protocol. Based on asyncio datagram protocol.
    """

    def __init__(self):
        """
        Initialization.
        """

        # Data type definition
        self.TYPE_UNKN  = 0
        self.TYPE_REG   = 1
        self.TYPE_UNREG = 2
        self.TYPE_KEP   = 3
        self.TYPE_EVE   = 4
        self.TYPE_SHK   = 5

        # Data type description
        self.TYPE = dict()
        self.TYPE[self.TYPE_UNKN] = 'UNKNOWN'
        self.TYPE[self.TYPE_REG] = 'REG'
        self.TYPE[self.TYPE_UNREG] = 'UNREG'
        self.TYPE[self.TYPE_KEP] = 'KEEPALIVE'
        self.TYPE[self.TYPE_EVE] = 'EVENT'
        self.TYPE[self.TYPE_SHK] = 'SHAKE'

        # Operation type
        self.OP_IGN     = 0
        self.OP_REFRESH = 1
        self.OP_REG     = 2
        self.OP_UNREG   = 3
        self.OP_BRDCST  = 4

        # Operation description
        self.OP = dict()
        self.OP[self.OP_IGN] = 'IGNORE'
        self.OP[self.OP_REFRESH] = 'REFRESH'
        self.OP[self.OP_REG] = 'REG'
        self.OP[self.OP_UNREG] = 'UNREG'
        self.OP[self.OP_BRDCST] = 'BROADCASTING'

        # Client pool
        self.client_pool = dict()

        self.ts_key = 'ts'
        self.nm_key = 'nm'

        # Client transport
        self.client_transport = None

        # Initializing logging
        logging.basicConfig(filename='/var/mysns/%d.log' % int(time.time()),
                            format='%(asctime)s %(message)s',
                            level=logging.DEBUG)


    def connection_made(self, transport):
        """
        Overriding the same-named function DatagramProtocol.connection_made
        from parent class, defining the behavior of client sending the data.

        Args:
            transport: In-coming transport.
        """

        self.client_transport = transport


    def datagram_received(self, data, addr):
        """
        Overriding the same-named function DatagramProtocol.datagram_received
        from parent class, defining the behavior of receiving data with
        datagram protocol.

        Args:
            data: A bytes object containing the incoming data.
            addr: The address of the peer sending the data.
        """

        logging.debug('==== Datagram Received, addr: %s, port: %d'
                      % (addr[0], addr[1]))

        logging.debug('Data Parsing.')
        parsed_data = self._data_parse(data)

        logging.debug('Operation Select.')
        operation = self._operation_select(parsed_data, addr)
        logging.debug('Operation %s is selected.' % (self.OP[operation]))

        logging.debug('Performing Operation.')
        self._perform_operation(operation, parsed_data, addr)

        logging.debug('Client pool: %s' % (str(self.client_pool)))
        logging.debug('==== Procedure DONE!')


    def _data_parse(self, data):
        """
        Parsing the incoming data.

        Args:
            data: The incoming data.

        Returns:
            Parsed data.
        """

        data_type = int(data[0])
        res = [data_type]

        if data_type == self.TYPE_REG:
            res.append(int(data[1]))
            res.append(data[2:(2 + int(data[1]))].decode())
        elif data_type == self.TYPE_UNREG or data_type == self.TYPE_KEP:
            pass
        elif data_type == self.TYPE_EVE:
            res.append(data[1:9])
        else:
            res[0] = self.TYPE_UNKN

        return res


    def _operation_select(self, data, addr):
        """
        Selecting operation according to parsed data.

        Args:
            data: Parsed data.
            addr: Client address.

        Returns:
            Operation types:
                OP_IGN     : Ignore
                OP_REFRESH : Refreshing
                OP_REG     : Registering
                OP_UNREG   : Unregistering
                OP_BRDCST  : Broadcasting
        """


        if addr in self.client_pool:
            if data[0] == self.TYPE_REG or data[0] == self.TYPE_KEP:
                return self.OP_REFRESH
            elif data[0] == self.TYPE_EVE:
                return self.OP_BRDCST
            elif data[0] == self.TYPE_UNREG:
                return self.OP_UNREG
            else:
                return self.OP_IGN
        else:
            if data[0] == self.TYPE_REG:
                return self.OP_REG
            else:
                return self.OP_IGN


    def _perform_operation(self, operation, data, addr):
        """
        Performing operation.

        Args:
            operation: Operation type.
            data: Parsed data.
            addr: Relative client address.
        """


        if addr in self.client_pool:
            if operation == self.OP_IGN:
                pass
            elif operation == self.OP_REFRESH:
                self._refresh(addr)
            elif operation == self.OP_REG:
                self._reg(addr, data[2])
            elif operation == self.OP_UNREG:
                self._unreg(addr)
            elif operation == self.OP_BRDCST:
                self._broadcast(addr, data[1])
            else:
                pass
        else:
            if operation == self.OP_REG:
                self._reg(addr, data[2])
            else:
                pass


    def _refresh(self, addr):
        """
        Refreshing the timestamp of client.

        Args:
            addr: The address to be refreshed.
        """

        if addr in self.client_pool:
            self.client_pool[addr][self.ts_key] = time.time()



    def _reg(self, addr, name):
        """
        Registering a new client.

        Args:
            addr: The address to be registered.
            name: The name of the client.
        """

        if addr in self.client_pool:
            self.client_pool[addr][self.ts_key] = time.time()
        else:
            self.client_pool[addr] = dict()
            self.client_pool[addr][self.nm_key] = name
            self.client_pool[addr][self.ts_key] = time.time()


    def _unreg(self, addr):
        """
        Unregistering a client.

        Args:
            addr: The address to be unregistered.
        """

        if addr in self.client_pool:
            del self.client_pool[addr]


    def _broadcast(self, addr, ts):
        """
        Broadcasting to all the client except addr.

        Args:
            addr: The in-coming client address.
            ts: The event timestamp.
        """

        if addr not in self.client_pool:
            return

        # Assembling data
        data = struct.pack('>B', self.TYPE_SHK)
        data = data + ts
        data = data + struct.pack('>B', len(self.client_pool[addr][self.nm_key]))
        data = data + self.client_pool[addr][self.nm_key].encode()

        ava_filter = lambda x : (time.time() - x[1][self.ts_key] < 20)
        self.client_pool = dict(filter(ava_filter, self.client_pool.items()))

        for key, value in self.client_pool.items():
            if key != addr:
                self.client_transport.sendto(data, key)
