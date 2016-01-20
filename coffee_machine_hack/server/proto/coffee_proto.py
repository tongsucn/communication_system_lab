#!/usr/bin/env python3


class CoffeeProtocol(object):
    """
    The coffee machine protocol, deal with the communication between server and
    Raspberry PI.
    """

    def __init__(self, addr, port):
        """
        Initializing address and port of the coffee machine.

        Args:
            addr: Address of the coffee machine.
            port: The port that the machine uses.
        """

        self.addr = addr
        self.port = port

        self.connected = False


    def conn(self):
        """
        Connect to the coffee machine. Flag connected will be set to True if
        connection is established successfully.

        Returns:
            True: Connection established.
            False: Fail to establish connection.
        """
        pass


    def control(self, cmd):
        """
        Send commands and control the coffee machine

        Args:
            cmd: The command to send. Please read coffee_cmd.py.

        Returns:
            Response from coffee machine/Arduino.
        """
        pass


    def disconn(self):
        """
        Disconnect from the coffee machine. Flag connected will be set to False
        after calling.
        """
        self.connected = False
