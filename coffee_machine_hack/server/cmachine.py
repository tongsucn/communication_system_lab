#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import socket
import logging

import cherrypy

from enum import Enum
from google.protobuf.message import DecodeError

from cproto import coffee_pb2 as CP
from cproto.cmd_list import CommandList as CL


class CoffeeErr(Enum):
    """
    Error code for coffee machine

    ==== Error list:
    OK:         Status OK, no error. It will be set in the response of
                self._control if the communication is correct. It will also be
                set in the response of other functions with responses if the
                correspondence operations are succeed.

    DEFAULT:    Default error. It will be set if unknown error happened or the
                Arduino complains the format of requests.

    TIMEOUT:    Timeout error. It will be set if timeout occurs when communicate
                with the Arduino.

    PB_DECODE:  Protobuf's decoder error. It will be set if the Protobuf cannot
                parse the response from the Arduino.

    WAS_ON:     It will be set when try turning on a machine which was already
                turned on.

    WAS_OFF:    It will be set when try turning on a machine which was already
                turned off.

    NOT_ON:     It will be set when coffee machine cannot be turned on.

    NOT_OFF:    It will be set when coffee machine cannot be turned off.

    NO_WATER:   It will be set when there is no water available.

    NO_BEANS:   It will be set when there are no beans available.

    NO_CUP:     It will be set when there is no cup available.

    NO_TRAY:    It will be set when there is no tray available.

    STS_TABLE:  It will be set if the response of Arduino is a status table.
    """

    # Error list
    OK          = 0
    DEFAULT     = 1
    TIMEOUT     = 2
    PB_DECODE   = 3
    WAS_ON      = 4
    WAS_OFF     = 5
    NOT_ON      = 6
    NOT_OFF     = 7
    NO_WATER    = 8
    NO_BEANS    = 9
    NO_CUP      = 10
    NO_TRAY     = 11
    NO_POWER    = 12
    STS_TABLE   = 13


class CoffeeMachine(object):
    """
    Coffee machine instance
    """

    # CoffeeErr alias
    WAS = {'ON' : CoffeeErr.WAS_ON,
           'OFF' : CoffeeErr.WAS_OFF}
    NOT = {'ON' : CoffeeErr.NOT_ON,
           'OFF' : CoffeeErr.NOT_OFF}
    NO = {'POWER' : CoffeeErr.NO_POWER,
          'WATER' : CoffeeErr.NO_WATER,
          'BEANS' : CoffeeErr.NO_BEANS,
          'CUP'   : CoffeeErr.NO_CUP,
          'TRAY' : CoffeeErr.NO_TRAY}


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


        # Connection timeout
        self.coffee_timeout = 120


        # Initializing logging
        self.log_path = './log'
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        self.log_file = os.path.join(self.log_path,
                                     'cmachine_%d.log' % (int(time.time())))

        logging.basicConfig(filename=self.log_file,
                            format='[%(levelname)s] %(asctime)s %(message)s',
                            level=logging.DEBUG)

        logging.info('Welcome!')
        logging.info('Initializing...')

        # A default product list
        self.product_list = [(1, 'Latte'), (2, 'Espresso'), (3, 'Cappuccino'),
                             (4, 'Milk coffee'), ('COFFEE', 'Coffee'),
                             ('STEAM', 'Steam')]
        self.product_list_file = product_list_file
        self.update_product_list()

        logging.info('Initialization Done!')


    def update_product_list(self, list_file = ''):
        """
        Parse products list from configuration file. Results will be stored in
        self.product_list. If the configuration file is not available, a default
        product list will be generated.

        If the list_file is specified, the function will parse the specified
        file. If error happened, the product list will not be updated.

        Args:
            list_file: product list file, default value is an empty string.
        """
        tar_file = list_file if len(list_file) else self.product_list_file

        if os.path.isfile(tar_file):
            with open(tar_file, 'r') as config_file:
                try:
                    cache_list = json.load(config_file)
                except json.decoder.JSONDecodeError:
                    logging.warning('File format error, use previous/default.')
                    cache_list = self.product_list

                # Format product list
                fmt = lambda x : (x['id'], x['name'])
                self.product_list = list(map(fmt, cache_list))
                logging.info('Product list:\n%s'
                             % json.dumps(self.product_list, indent = 2))
        else:
            logging.warning('Product file not exist, use previous/default.')


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def ls_products(self):
        """
        Provide the list of products. List is not sorted.

        Returns:
            Product lists that the coffee machine provides. In format:
                [(1, 'Product 1'), (2, 'Product 2'), ...,
                ('COFFEE', 'Coffee'), ...]
        """
        return {key : name for key, name in self.product_list}


    def _control(self, cmd_type, cmd):
        """
        Control the coffee machine with some commands. After calling, the
        function will block until there is response.

        Communication-related exceptions are handled here, including timeout
        and Protobuf's error. If the communication is normal, the response
        type and relative content (e.g. if the operation succeed) should be
        handled in the functions that called this function.

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

        recv_msg = None
        sock.sendto(sent_msg, (self.c_addr, self.c_port))
        try:
            recv_msg = sock.recv(1024)

            pb_resp = CP.Response()
            pb_resp.ParseFromString(recv_msg)
            resp = (CoffeeErr.OK, pb_resp)
        except socket.timeout:
            resp = (CoffeeErr.TIMEOUT,
                    'Cannot communicate with coffee machine')

            logging.error('Timeout when communicate with coffee Arduino.')
        except DecodeError:
            resp = (CoffeeErr.PB_DECODE,
                    'Protobuf error: Cannot parse response.')

            logging.error('Protobuf DecodeError when decode Arduino response.')
        finally:
            sock.close()

        return resp


    @cherrypy.expose
    def turn(self, status):
        res = self._turn(status)
        return res[1]


    def _turn(self, status):
        """
        Turn on or off  the coffee machine.

        ATTENTION: If the input argument's format is INCORRECT, the TypeError
                   exception will be raised.

        Examples:
            self.turn('ON')     # Turn on
            self.turn('OFF')    # Turn off
            self.turn(OTHER)    # Raise TypeError exception!!

        Args:
            status: Target status, either 'ON' or 'OFF'

        Returns:
            Format (ERR_CODE, DETAIL):
                ERR_CODE: Error code defined in class CoffeeErr
                DETAIL: A human-readable description for result
            Potential:
                (CoffeeErr.OK, str)
                (CoffeeErr.DEFAULT, str)
                (CoffeeErr.TIMEOUT, str)
                (CoffeeErr.PB_DECODE, str)
                (CoffeeErr.WAS_ON, str)
                (CoffeeErr.WAS_OFF, str)
                (CoffeeErr.NOT_ON, str)
                (CoffeeErr.NOT_OFF, str)
        """
        resp = None
        accepted = ['ON', 'OFF']

        if type(status) is not str or status not in accepted:
            raise TypeError('Incorrect status value. Please either ON or OFF')
        logging.info('Coffee machine status checking.')
        status_table = self.check('ALL')

        logging.info('Try turning %s the coffee machine.' % status)
        if status_table[0] != CoffeeErr.STS_TABLE:
            resp = status_table
        # Power status checking need to be fixed
        elif False:
            # elif status_table[1]['POWER'] == (status == 'ON'):
            resp = (self.WAS[status],
                    'Coffee machine was already %s' % status)

            logging.warning('Coffee machine was already %s.' % status)
        else:
            # Send command to machine and wait for response
            raw_resp = self._control(CP.CoffeeCommand.OPERATION,
                                     CL.TURN[status])

            # Parse parsed response from self._control
            if raw_resp[0] == CoffeeErr.OK:
                # Parsing CORRECT. Parse Protobuf message instance.
                if raw_resp[1].type == CP.Response.OK:
                    resp = (CoffeeErr.OK,
                            'Coffee machine is now turned %s' % status)

                    logging.info('Coffee machine is now turned %s.' % status)
                elif raw_resp[1].type == CP.Response.OPERATION_ERR:
                    resp = (self.NOT[status],
                            'Coffee machine cannot be turned %s' % status)

                    logging.error('Coffee machine cannot be turned %s.'
                                  % status)
                else:
                    resp = self._err_format()
            else:
                # Parsing INCORRECT. Response error message from self._control
                resp = raw_resp

        return resp


    @cherrypy.expose
    def makeById(self, pid):
        logging.info('Making product: ' + pid)
        try:
            iPid = int(pid)
        except ValueError:
            logging.error('Invalid input.')
            return
        prod = None
        for p in self.product_list:
            if p[0] == iPid:
                prod = p
        if prod:
            logging.info('Calling make with ' + prod[1])
            res = self.make(prod)
            return res[1]
        else:
            return 0


    def make(self, product):
        """
        Make a specified product, it could be products 1 to 4, coffee and steam.
        Before making product, it will firstly check beans (not support yet) and
        water availability. If these two are not available, relative errors will
        be returned.

        Examples (default generated product list):
            self.make(self.product_list[0])     # Make product 1
            self.make(self.product_list[4])     # Make coffee

        Args:
            product: The product specification, in tuple format:
                (id, name)
                id: int or str, the product's ID, range [1, len(CC.PRODUCTS)]
                    or 'COFFEE' or 'STEAM'
                name: str, the product's name

        Returns:
            Format (ERR_CODE, DETAIL):
                ERR_CODE: Error code defined in class CoffeeErr
                DETAIL: A human-readable description for result
            Potential:
                (CoffeeErr.OK, str)
                (CoffeeErr.DEFAULT, str)
                (CoffeeErr.TIMEOUT, str)
                (CoffeeErr.PB_DECODE, str)
                (CoffeeErr.NO_WATER, str)
                (CoffeeErr.NO_BEANS, str)   # Not support yet
        """
        resp = None
        product_id = product[0]
        product_name = product[1]
        logging.info('Coffee machine status checking.')
        status_table = self.check('ALL')

        logging.info('Make product: %s.' % product_name)
        if status_table[0] != CoffeeErr.STS_TABLE:
            resp = status_table
        elif False:
            # elif status_table[1]['POWER'] == (status == 'ON'):
            resp = (CoffeeErr.WAS_OFF,
                    'Machine was turned OFF, turn it ON before making product')

            logging.warning('Coffee machine was off when try making product: '
                            '%s.' % product_name)
        else:
            # Before operation, check water tank
            resp_water = self.check('WATER')
            if resp_water[0] == CoffeeErr.NO_WATER:
                return resp_water

            # Send command to machine and wait for response
            raw_resp = self._control(CP.CoffeeCommand.OPERATION,
                                     CL.PRODUCTS[product_id])

            # Parse parsed response from self._control
            if raw_resp[0] == CoffeeErr.OK:
                # Parsing CORRECT. Parse Protobuf message instance.
                if raw_resp[1].type == CP.Response.OK:
                    resp = (CoffeeErr.OK, '%s is prepared' % product_name)

                    logging.info('%s is prepared.' % product_name)
                elif raw_resp[1].type == CP.Response.OPERATION_ERR:
                    resp = (CoffeeErr.DEFAULT, 'Cannot make %s' % product_name)
                    logging.error('Cannot make %s' % product_name)
                else:
                    resp = self._err_format()
            else:
                # Parsing INCORRECT. Response error message from self._control
                resp = raw_resp

        return resp


    def is_on(self):
        """
        Return the status of coffee machine.

        Returns:
            True: The coffee machine is on.
            False: The coffee machine is off.
        """
        resp = self.check('POWER')
        return True if resp[0] == CoffeeErr.OK else False


    def check(self, target):
        """
        Check water tank, beans (not support yet) and cup (not support yet)

        ATTENTION: If the input argument's format is INCORRECT, the TypeError
                   exception will be raised.

        Examples:
            self.check('WATER')   # Check water availability
            self.check(OTHER)     # Raise TypeError exception!!

        Args:
            target: Target to be checked:
                'ALL': power, water, tray, beans (beans not support yet)
                'POWER': machine status
                'WATER': water availability
                'TRAY': tray availability
                'BEANS': bean availability (not support yet)
                'CUP': cup existence (not support yet)

        Returns:
            Format (ERR_CODE, DETAIL):
                ERR_CODE: Error code defined in class CoffeeErr
                DETAIL: A human-readable description for result or a dict
                        for storing multiple results (only for STS_TABLE).
            Potential:
                (CoffeeErr.OK, str)
                (CoffeeErr.DEFAULT, str)
                (CoffeeErr.TIMEOUT, str)
                (CoffeeErr.PB_DECODE, str)
                (CoffeeErr.NO_POWER, str)
                (CoffeeErr.NO_WATER, str)
                (CoffeeErr.NO_TRAY, str)
                (CoffeeErr.NO_BEANS, str)   # Not support yet
                (CoffeeErr.NO_CUP, str)     # Not support yet
                (CoffeeErr.STS_TABLE, dict)
        """
        resp = None
        accepted = ['ALL', 'POWER', 'WATER', 'BEANS', 'CUP', 'TRAY']
        not_support = ['BEANS', 'CUP']
        err_idx = {'POWER' : CoffeeErr.NO_POWER,
                   'WATER' : CoffeeErr.NO_WATER,
                   'BEANS' : CoffeeErr.NO_BEANS,
                   'CUP' : CoffeeErr.NO_CUP,
                   'TRAY' : CoffeeErr.NO_TRAY}

        if type(target) is not str or target not in accepted:
            raise TypeError('Incorrect status value. '
                            'Please use these values: %s' % ','.join(accepted))

        logging.info('Try checking %s.' % target)
        if target in not_support:
            # Cup detection or beans checking, not support yet
            resp = (CoffeeErr.DEFAULT,
                    'Checking %s is not supported yet' % target)
            logging.warning('Checking %s is not supported yet.' % target)
        else:
            # Send command to machine and wait for response
            raw_resp = self._control(CP.CoffeeCommand.QUERY, CL.CHK[target])

            # Parse parsed response from self._control
            if raw_resp[0] == CoffeeErr.OK:
                # Getting status table
                status_idx = {'POWER' : raw_resp[1].results.POWER,
                              'WATER' : raw_resp[1].results.WATER,
                              'BEANS' : raw_resp[1].results.POWER,
                              'CUP' : True,
                              'TRAY' : raw_resp[1].results.TRAY}

                if raw_resp[1].type == CP.Response.RESULT:
                    if target == 'ALL':
                        resp = (CoffeeErr.STS_TABLE, status_idx)
                        logging.info('Got status table.')
                    else:
                        if status_idx[target]:
                            resp = (CoffeeErr.OK, '%s is available' % target)
                            logging.info('%s is available.' % target)
                        else:
                            resp = (err_idx[target], '%s is not available.'
                                    % target)
                            logging.error('%s is not available.' % target)
                else:
                    resp = self._err_format()
            else:
                resp = raw_resp
        return resp


    def checkWeb(self, target):
        res = self.check(target)
        if res[0] == CoffeeErr.OK:
            return res[1]
        return False


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        res = {
            "status": self.status,
            "product_list": [],
        }
        if self.status == True:
                res.update({
            	     "has_water": self.checkWeb('WATER'),
                     "has_bean": self.checkWeb('BEANS'),
            	     "has_tray":self.checkWeb('TRAY'),
            	     "has_cup": self.checkWeb('CUP'),
                })
        if self.product_list:
            res["product_list"] = self.product_list
        return res


    def _err_format(self):
        """
        Provide Arduino's complain about format of request and record log.

        Returns:
            (CoffeeErr.DEFAULT, 'Arduino complains about format of request')
        """
        logging.error('Arduino complains about format of request.')

        return (CoffeeErr.DEFAULT, 'Arduino complains about format of request')
