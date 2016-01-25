#!/usr/bin/env python3


import os
import time
import json
import socket
import logging
from enum import Enum

import google.protobuf.message.DecodeError

from cproto import coffee_pb2 as CP
from cproto.cmd_list import CommandList as CL


class CoffeeErr(Enum):
    """
    Error code for coffee machine

    OK:         Status OK, no error
    DEFAULT:    Default error
    TIMEOUT:    Timeout error, occurs during communication with Arduino
    PB_DECODE:  Protobuf's decoder error
    WAS_ON:     The machine has been turned on
    WAS_OFF:    The machine has been turned off
    NO_ON:      The machine cannot be turned on
    NO_OFF:     The machine cannot be turned off
    NO_WATER:   No water available
    NO_BEAN:    No beans available
    """
    OK          = 0
    DEFAULT     = 1
    TIMEOUT     = 2
    PB_DECODE   = 3
    WAS_ON      = 4
    WAS_OFF     = 5
    NO_ON       = 6
    NO_OFF      = 7
    NO_WATER    = 8
    NO_BEAN     = 9


class CoffeeMachine(object):
    """
    Coffee machine instance
    """

    def __init__(self, addr, port, product_list_file):
        """
        Initializing coffee machine setting.

        Args:
            addr: Address of the coffee machine.
            port: The port that the machine uses.
        """

        # Variables about the coffee machine
        # Address of the coffee machine
        self.c_addr = addr
        self.c_port = port

        # Coffee machine status
        self.status = False

        # Connection timeout
        self.coffee_timeout = 120

        # A default product list
        self.product_list = [{'name': 'latte', 'id': 1},
                             {'name': 'espresso', 'id': 2},
                             {'name': 'cappuccino', 'id': 3},
                             {'name': 'milk coffee', 'id': 4}]

        self.product_list_file = product_list_file

        # Initializing logging
        self.log_path = './log'
        if not os.exists(self.log_path):
            os.mkdir(self.log_path)

        self.log_file = os.path.join(self.log_path,
                                     'cmachine_%d.log' % (int(time.time())))

        logging.basicConfig(filename=self.log_file,
                            format='%(asctime)s %(message)s',
                            level=logging.DEBUG)


    def _parse_product_list(self):
        """
        Parse products list from configuration file. Results will be stored in
        self.product_list. If the configuration file is not available, a default
        product list will be generated
        """
        if os.path.isfile(self.product_list_file):
            with open(self.product_list_file, 'r') as config_file:
                try:
                    cache_list = json.load(config_file)
                except json.JSONDecoder:
                    logging.warning('Product file format error, use default.')
                    cache_list = self.product_list

                self.product_list = cache_list
                logging.info('Product list:\n%s'
                             % json.dumps(self.product_list, indent=2))
        else:
            logging.warning('Product list file does not exist, use default.')


    def _control(self, cmd_type, cmd):
        """
        Control the coffee machine with some commands. After calling, the
        function will block until there is response.

        Args:
            cmd_type: The command type from CP.CoffeeCommand.CommandType
            cmd: The command from cmd_list.CommandList

        Returns:
            Format (ERR_CODE, DETAIL):
                ERR_CODE: Error code defined in class CoffeeErr
                DETAIL:
                    Either a human-readable description for the error
                    or the Protobuf result object for response from Arduino.
            Potential:
                (CoffeeErr.OK, coffee_pb2.Response)
                (CoffeeErr.TIMEOUT, str)
                (CoffeeErr.PB_DECODE, str)
        """
        # Preparing Protobuf object
        pb_cmd = CP.CoffeeCommand()
        pb_cmd.type = cmd_type
        pb_cmd.command = cmd
        sent_msg = pb_cmd.SerializeToString()

        # Network communication
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        sock.settimeout(self.coffee_timeout)

        sock.sendto(sent_msg, (self.c_addr, self.c_port))
        try:
            (recv_msg, (remote_addr, remote_port)) = sock.recvfrom(1024)
        except socket.timeout:
            resp = (CoffeeErr.TIMEOUT,
                    'Cannot communicate with coffee machine')

            logging.error('Timeout when communicate with coffee Arduino.')
        finally:
            sock.close()

        try:
            pb_resp = CP.Response()
            pb_resp.ParseFromString(recv_msg)
            resp = (CoffeeErr.OK, pb_resp)
        except google.protobuf.message.DecodeError:
            resp = (CoffeeErr.PB_DECODE,
                    'Cannot communicate with coffee machine')

            logging.error('Protobuf DecodeError when decoding Arduino resp.')

        return resp


    def turn_on(self):
        """
        Turn on the coffee machine. Flag status will be set to True after
        calling.

        Returns:
            Format (ERR_CODE, DETAIL):
                ERR_CODE: Error code defined in class CoffeeErr
                DETAIL: A human-readable description for result.
            Potential:
                (CoffeeErr.OK, str)
                (CoffeeErr.DEFAULT, str)
                (CoffeeErr.TIMEOUT, str)
                (CoffeeErr.PB_DECODE, str)
                (CoffeeErr.WAS_ON, str)
                (CoffeeErr.NO_ON, str)
        """
        resp = None

        logging.info('Try turning on the coffee machine')
        if (self.status):
            resp = (CoffeeErr.WAS_ON, 'Coffee machine has been turned ON')

            logging.warning('Coffee machine has been turned on.')
        else:
            raw_resp = self._control(CP.CoffeeCommand.OPERATION,
                                     CL.CommandList.TURN_ON)

            # Parsing Protobuf object
            if raw_resp[0] == CoffeeErr.OK:
                if raw_resp[1].type == CP.Response.OK:
                    resp = (CoffeeErr.OK, 'Coffee machine is now turned ON')
                    self.status = True

                    logging.info('Coffee machine is not turned on.')
                elif raw_resp[1].type == CP.Response.FORMAT_UNKN:
                    resp = (CoffeeErr.DEFAULT,
                            'Arduino complains about format of request')

                    logging.error('Arduino complains about format of request.')
                else:
                    resp = (CoffeeErr.NO_ON,
                            'Coffee machine cannot be turned on')

                    logging.error('Coffee machine cannot be turned on.')
            else:
                resp = raw_resp

        return resp


    def turn_off(self):
        """
        Turn off the coffee machine. Flag status will be set to False after
        calling.

        Returns:
            Format (ERR_CODE, DETAIL):
                ERR_CODE: Error code defined in class CoffeeErr
                DETAIL: A human-readable description for result.
            Potential:
                (CoffeeErr.OK, str)
                (CoffeeErr.DEFAULT, str)
                (CoffeeErr.TIMEOUT, str)
                (CoffeeErr.PB_DECODE, str)
                (CoffeeErr.WAS_OFF, str)
                (CoffeeErr.NO_OFF, str)
        """
        resp = None

        logging.info('Try turning off the coffee machine')
        if (not self.status):
            resp = (CoffeeErr.WAS_OFF, 'Coffee machine has been turned OFF')

            logging.warning('Coffee machine has been turned off.')
        else:
            raw_resp = self._control(CP.CoffeeCommand.OPERATION,
                                     CL.CommandList.TURN_OFF)

            # Parsing Protobuf object
            if raw_resp[0] == CoffeeErr.OK:
                if raw_resp[1].type == CP.Response.OK:
                    resp = (CoffeeErr.OK, 'Coffee machine is now turned OFF')
                    self.status = False

                    logging.info('Coffee machine is not turned off.')
                elif raw_resp[1].type == CP.Response.FORMAT_UNKN:
                    resp = (CoffeeErr.DEFAULT,
                            'Arduino complains about format of request')

                    logging.error('Arduino complains about format of request.')
                else:
                    resp = (CoffeeErr.NO_OFF,
                            'Coffee machine cannot be turned off')

                    logging.error('Coffee machine cannot be turned off.')
            else:
                resp = raw_resp

        return resp


    def clean(self):
        """
        Clean the coffee machine.

        Returns:
            Format (ERR_CODE, DETAIL):
                ERR_CODE: Error code defined in class CoffeeErr
                DETAIL: A human-readable description for result.
            Potential:
                (CoffeeErr.OK, str)
                (CoffeeErr.DEFAULT, str)
                (CoffeeErr.TIMEOUT, str)
                (CoffeeErr.PB_DECODE, str)
                (CoffeeErr.WAS_OFF, str)
        """
        resp = None

        logging.info('Try cleaning the coffee machine')
        if (not self.status):
            resp = (CoffeeErr.WAS_OFF,
                    'Machine was turned OFF, turn it ON before cleaning')

            logging.warning('Coffee machine was turned off\
                            when try cleaning it.')
        else:
            raw_resp = self._control(CP.CoffeeCommand.OPERATION,
                                     CL.CommandList.CLEANING)

            # Parsing Protobuf object
            if raw_resp[0] == CoffeeErr.OK:
                if raw_resp[1].type == CP.Response.OK:
                    resp = (CoffeeErr.OK, 'Cleaning finished')
                    self.status = True

                    logging.info('Cleaning finished')
                elif raw_resp[1].type == CP.Response.FORMAT_UNKN:
                    resp = (CoffeeErr.DEFAULT,
                            'Arduino complains about format of request')

                    logging.error('Arduino complains about format of request.')
                else:
                    resp = (CoffeeErr.TURN_OFF,
                            'Coffee machine cannot be turned off')

                    logging.error('Coffee machine cannot be turned off.')
            else:
                resp = raw_resp

        return resp


    def product_list(self):
        """
        Provide the list of products.

        Returns:
            Product lists that the coffee machine provides. In format:
                [(1, 'Product 1'), (2, 'Product 2'), ...]
        """
        self._parse_product_list()
        return self.product_list


    def make_product(self, product):
        """
        Make a specified product.

        Args:
            product: The product specification, in tuple format:
                (id, name)
                id: int, the product's ID, range [1, 7]
                name: str, the product's name

        Return:
            Either None (coffee machine N.A.) or description of operation
            results.
        """
        pass


    def make_steam(self):
        """
        Make stream.

        Returns:
            Either None (coffee machine N.A.) or description of operation
            results.
        """
        pass


    def make_coffee(self):
        """
        Make a cup of coffee.

        Return:
            Either None (coffee machine N.A.) or description of operation
            results.
        """
        pass


    def is_on(self):
        """
        Return the status of coffee machine.

        Returns:
            True: The coffee machine is on.
            False: The coffee machine is off.
        """
        pass


    def has_water(self):
        """
        Check water tank.

        Returns:
            True: The coffee machine is on.
            False: The coffee machine is off.
        """
        pass


    def has_bean(self):
        """
        Check bean available.

        Returns:
            True: The coffee machine is on.
            False: The coffee machine is off.
        """
        pass


    def has_cup(self):
        """
        Reserve for CV task.
        """
        pass
