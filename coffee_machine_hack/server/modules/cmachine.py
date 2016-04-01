#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import socket
import logging
import datetime
from enum import Enum
from threading import Thread
import cherrypy

from google.protobuf.message import DecodeError
from cproto import coffee_pb2 as CP
from cproto.cmd_list import CommandList as CL

from modules import users

"""
   Communication module between Arduino + server

   Implemented API-Endpoints
    /machine/get        - Returns current status of the machine
    /machine/makeById   - Start brewing product pid if all requirements are met
    /machine/turn       - Sets powerstate of the machine
    /machine/ls_products- Returns used profile list as dict
"""


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

    # Variables about the coffee machine
    # Address of the coffee machine
    ip_address = "192.168.10.233"
    ip_port = 8233

    # Coffee machine status
    status = False

    # Connection timeout
    coffee_timeout = 10

    # Current status of the machine. Updated with polling-thread
    statusTable = {
        'POWER' : False,
        'WATER' : False,
        'BEANS' : False,
        'CUP'   : False,
        'TRAY'  : False
    }

    # Flag to determine wether the statusThread is active / should Terminate
    statusActive = False

    # Timestamp of the last brewed coffee
    coffee_timestamp = datetime.datetime.now()

    # Timeout (in s) until a new coffee can be brewed
    brew_timeout = 45

    def __init__(self):
        """
            Initializing coffee machine setting.
        """

        logging.info('Initializing coffeemachine')

        # A default product list
        self.product_list = [(1, 'Latte'), (2, 'Espresso'), (3, 'Cappuccino'),
                             (4, 'Milk coffee'), ('COFFEE', 'Coffee'),
                             ('STEAM', 'Steam')]
        logging.error('Starting thread')
        Thread(target=self.statusThread).start()

        logging.info('Initialization Done!')

    def update_product_list(self, products):
        """
        Sets the current Product list. Results will be stored in
        self.product_list. If error happened, the product list will not be updated.

        Args:
            products: New product list.
        """
        if not products:
            return

        # Format product list
        self.product_list = list(map(lambda x: (x['id'], x['name']), products))
        logging.info('Product list:\n%s', json.dumps(self.product_list, indent=2))

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
        sock.sendto(sent_msg, (self.ip_address, self.ip_port))
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
                (CoffeeErr.NO_WATER, str))
        """
        resp = None
        accepted = ['ON', 'OFF']

        if not isinstance(status, str) or status not in accepted:
            raise TypeError('Incorrect status value. Please either ON or OFF')
        logging.info('Coffee machine status checking.')
        status_table = self.statusTable

        logging.info('Try turning %s the coffee machine.', status)
        if status_table['POWER'] == (status == 'ON'):
            resp = (self.WAS[status],
                    'Coffee machine was already %s', status)

            logging.warning('Coffee machine was already %s.', status)
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

                    logging.info('Coffee machine is now turned %s.', status)
                elif raw_resp[1].type == CP.Response.OPERATION_ERR:
                    resp = (self.NOT[status],
                            'Coffee machine cannot be turned %s' % status)

                    logging.error('Coffee machine cannot be turned %s.', status)
                else:
                    resp = self._err_format()
            else:
                # Parsing INCORRECT. Response error message from self._control
                resp = raw_resp

        return resp

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
        status_table = self.statusTable

        logging.info('Make product: %s.', product_name)
        if not status_table['POWER']:
            resp = (CoffeeErr.WAS_OFF,
                    'Machine was turned OFF, turn it ON before making product')

            logging.warning('Coffee machine was off when try making product: '
                            '%s.', product_name)
        else:
            # Before operation, check machine status
            if not status_table['WATER']:
                logging.error('Cannot make product %s, because no water.', product_name)
                return (CoffeeErr.NO_WATER,
                        'Cannot make product %s, because no water'
                        % product_name)
            if not status_table['BEANS']:
                logging.error('Cannot make product %s, because no beans.', product_name)
                return (CoffeeErr.NO_BEANS,
                        'Cannot make product %s, because no beans'
                        % product_name)
            if not status_table['TRAY']:
                logging.error('Cannot make product %s, because no tray.', product_name)
                return (CoffeeErr.NO_TRAY,
                        'Cannot make product %s, because no tray'
                        % product_name)

            # Update timestamp
            tdelta = datetime.datetime.now() - self.coffee_timestamp
            if tdelta < datetime.timedelta(seconds=self.brew_timeout):
                logging.error('Cannot make product %s, because another coffee is brewing.', product_name)
                return (CoffeeErr.TIMEOUT, 'Cannot make product {}, because another coffee is brewing. Try again in {} seconds.'.format(
                    product_name, int(self.brew_timeout - tdelta.total_seconds())))

            self.coffee_timestamp = datetime.datetime.now()

            # Send command to machine and wait for response
            raw_resp = self._control(CP.CoffeeCommand.OPERATION,
                                     CL.PRODUCTS[product_id])

            # Parse parsed response from self._control
            if raw_resp[0] == CoffeeErr.OK:
                # Parsing CORRECT. Parse Protobuf message instance.
                if raw_resp[1].type == CP.Response.OK:
                    resp = (CoffeeErr.OK, '%s is prepared' % product_name)

                    logging.info('%s is prepared.', product_name)
                elif raw_resp[1].type == CP.Response.OPERATION_ERR:
                    resp = (CoffeeErr.DEFAULT, 'Cannot make %s' % product_name)
                    logging.error('Cannot make %s', product_name)
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

        if not isinstance(target, str) or target not in accepted:
            raise TypeError('Incorrect status value. '
                            'Please use these values: %s' % ','.join(accepted))

        logging.info('Try checking %s.', target)
        if target in not_support:
            # Cup detection or beans checking, not support yet
            resp = (CoffeeErr.DEFAULT,
                    'Checking %s is not supported yet' % target)
            logging.warning('Checking %s is not supported yet.', target)
        else:
            # Send command to machine and wait for response
            raw_resp = self._control(CP.CoffeeCommand.QUERY, CL.CHK[target])

            # Parse parsed response from self._control
            if raw_resp[0] == CoffeeErr.OK:
                # Getting status table
                status_idx = {'POWER' : raw_resp[1].results.POWER,
                              'WATER' : raw_resp[1].results.WATER,
                              'BEANS' : raw_resp[1].results.BEANS,
                              'CUP' : True,
                              'TRAY' : raw_resp[1].results.TRAY}

                if raw_resp[1].type == CP.Response.RESULT:
                    if target == 'ALL':
                        resp = (CoffeeErr.STS_TABLE, status_idx)
                        logging.info('Got status table.')
                    else:
                        if status_idx[target]:
                            resp = (CoffeeErr.OK, '%s is available' % target)
                            logging.info('%s is available.', target)
                        else:
                            resp = (err_idx[target], '%s is not available.'
                                    % target)
                            logging.error('%s is not available.', target)
                else:
                    resp = self._err_format()
            else:
                resp = raw_resp
        return resp

    def statusThread(self):
        """ Status-thread polling the Arduino for current state. Runs until statusActive == False """
        self.statusActive = True
        while self.statusActive:
            res = self.check('ALL')
            if res[0] == CoffeeErr.STS_TABLE:
                self.statusTable = res[1]
            else:
                logging.error('Failed to update: ' + str(res[0]))
                logging.error(res[1])
            time.sleep(1)

    def shutdown(self):
        logging.info('Shutting down cMachine')
        self.statusActive = False

    def checkWeb(self, target):
        """ Helper function to format the return-value of check as JSON-encodable value """
        res = self.check(target)
        if res[0] == CoffeeErr.STS_TABLE:
            return res[1]
        return False

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def ls_products(self):
        """
        Provide the directory of products. List is not sorted.

        Returns:
            Product lists that the coffee machine provides. In format:
                {pid: name}
        """
        return {key: name for key, name in self.product_list}

    @cherrypy.expose
    @users.require()
    def turn(self, status):
        res = self._turn(status)
        return res[1]

    @cherrypy.expose
    @users.require()
    def makeById(self, pid):
        """ API-Entrypoint for brewing a coffee. Checks all valid prerequisites + 
            starts the brewing process if they're met """
        logging.info('Making product: ' + pid)

        if self.statusTable['WATER'] == False:
            return 'Requirements not met: No Water available',
        if self.statusTable['BEANS'] == False:
            return 'Requirements not met: No Beans available',
        if self.statusTable['TRAY'] == False:
            return 'Requirements not met:  Tray was removed from the system'
        try:
            iPid = int(pid)
        except ValueError:
            logging.error('Invalid input.')
            return 'Invalid input.'
        prod = None
        for p in self.product_list:
            if p[0] == iPid:
                prod = p
        if prod:
            logging.info('Calling make with ' + prod[1])
            res = self.make(prod)
            if res[1] == CoffeeErr.OK:
                users.addCount(prod)
                return "1"
            return res[1]
        else:
            return 'Invalid Product.'

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        """
            Returns the current status of the machine (excluding cupDetection) as JSON
        """
        res = {
            "status": self.statusTable['POWER'],
            "has_water": self.statusTable['WATER'],
            "has_bean": self.statusTable['BEANS'],
            "has_tray": self.statusTable['TRAY'],
            "product_list": []
        }
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
