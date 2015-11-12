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


class SensorNetProtocol(asyncio.DatagramProtocol):
    """
    Sensor Network Protocol. Based on datagram protocol.
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

        # Operation type
        self.OP_IGN     = 0
        self.OP_REFRESH = 1
        self.OP_REG     = 2
        self.OP_UNREG   = 3
        self.OP_BRDCST  = 4

        # Client pool
        self.client_pool = dict()

        self.ts_key = 'timestamp'
        self.nm_key = 'name'
        self.ava_key = 'available'

        # Client transport
        self.client_transport = None


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
            addr:
                The address of the peer sending the data.

        Returns:
            The parsed data, list type, the first element indicate the type of
            this data:
                IGN:        Ignore
                REFRESH:    Keep alive signal
                REG:        Registering
                UNREG:      Unregristering
                BRDCST:     Broadcasting

        """

        parsed_data = self._data_parse(data)
        operation = self._operation_select(parsed_data, addr)
        self._perform_operation(operation, parsed_datta, addr)


    async def _data_parse(self, data):
        """
        Parsing the incoming data.

        Args:
            data: The incoming data.
        """

        data_type = int(data[0])
        res = [data_type]

        if data_type == self.TYPE_REG:
            res.append(int(data[1]))
            res.append(data[2:(2 + int(data[1]))].decode())
        elif data_type == self.TYPE_UNREG or data_type == self.KEP:
            pass
        elif data_type == self.EVE:
            res.append(data[1:9])
        else:
            res[0] = self.TYPE_UNKN

        return res


    async def _operation_select(self, data, addr):
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

        if addr in self.client_pool and self.client_pool[addr][self.ava_key]:
            if data[0] == self.TYPE_REG or self.TYPE_KEP:
                return self.OP_REFRESH
            elif data[0] == self.TYPE_EVE:
                return self.OP_BRDCST
            elif data[0] == self.TYPE_UNREG:
                return self.OP_UNREG
            else:
                return self.OP_IGN
        elif addr in self.client_pool:
            if data[0] == self.TYPE_REG:
                return self.OP_REG
            else:
                return self.OP_IGN


    async def _perform_operation(self, operation, data, addr):
        """
        Performing operation.

        Args:
            operation: Operation type.
            data: Parsed data.
            addr: Relative client address.
        """

        if addr in self.client_pool and self.client_pool[addr][self.ava_key]:
            if operation == self.OP_IGN:
                pass
            elif operation == self.OP_REFRESH:
                self._refresh(addr)
            elif operation == self.OP_REG:
                self._reg(addr, data[2])
            elif operation == self.OP_UNREG:
                self._unreg(addr)
            elif operation == self.OP_BRDCST:
                await self._broadcast(addr, data[1])
            else:
                pass


    def _refresh(self, addr):
        """
        Refreshing the timestamp of client.

        Args:
            addr: The address to be refreshed.
        """

        if addr in self.client_pool and self.client_pool[addr][self.ava_key]:
            self.client_pool[addr]['timestamp'] = time.time()


    def _reg(self, addr, name):
        """
        Registering a new client.

        Args:
            addr: The address to be registered.
            name: The name of the client.
        """

        if addr in self.client_pool:
            self.client_pool[addr][self.ts_key] = time.time()
            self.client_pool[addr][self.ava_key] = True
        else:
            self.client_pool[addr] = dict()
            self.client_pool[addr][self.nm_key] = name
            self.client_pool[addr][self.ts_key] = time.time()
            self.client_pool[addr][self.ava_key] = True


    def _unreg(self, addr):
        """
        Unregistering a client.

        Args:
            addr: The address to be unregistered.
        """

        if addr in self.client_pool:
            self.client_pool[addr][self.ava_key] = False
            del self.client_pool[addr]


    async def _broadcast(self, addr, ts):
        """
        Broadcasting to all the client except addr.

        Args:
            addr: The in-coming client address.
            ts: The event timestamp.
        """

        if addr not in self.client_pool or not self.client_pool[addr][self.ava_key]:
            return

        # Assembling data
        data = struct.pack('>B', self.TYPE_SHK)
        data = data + ts
        data = data + struct.pack('>B', len(self.client_pool[addr][self.nm_key]))
        data = data + self.client_pool[addr][self.nm_key].encode()

        for key, value in self.items():
            if key != addr:
                life = time.time() - value[self.ts_key]
                if life < 20 and value[self.ava_key]:
                    self.transport.sendto(data, addr)
                elif life >= 20:
                    self._unreg(addr)
