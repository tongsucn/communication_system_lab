#!/usr/bin/env python3
# Communication Systems Lab
# Assignment 4
# Task 4.3
# Author: Tong, Michael
# ##############################
# Description:
# Protocol for switching plugs
#

class SwitchProtocol(object):
    """
    The protocol for switch control.
    """

    def __init__(self):
        """
        Definition of protocol information.

        |A |  B  |  C  |D |E |  (F)  |
        |--|-----|-----|--|--|----...|

        A: The request type:
            00: Refresh or Register from Raspberry PI
            01:
                Control a plug with house code in B and code in C,
                the status is recorded in D
            10: Delete a plug with house code in B and code in C
            11:
                Add a plug with house code in B, code in C and name in F,
                the length of name is in D and E
        B: The house code
        C: The code
        D: A == 01: the status, A == 11: the name length (first part)
        E: A == 11: the name length (second part)
        F: Optional, plug name, max. length 16 bytes
        """

        # Protocol length
        self.PROTO_MIN_LEN          = 2
        self.PROTO_MAX_LEN          = 18
        self.PROTO_BIT_LEN          = 8 * self.PROTO_MIN_LEN

        self.PROTO_TYPE_BIT_LEN     = 2
        self.PROTO_HOUSE_BIT_LEN    = 5
        self.PROTO_CODE_BIT_LEN     = 5
        self.PROTO_STATUS_BIT_LEN   = 2
        self.PROTO_RESV_BIT_LEN     = 2

        # The requested operation types
        self.OP_REFRESH = 0
        self.OP_CONTROL = 1
        self.OP_DELETE  = 2
        self.OP_ADD     = 3
        self.OP_REG     = 4

        # The plug information
        self.PLUG_DEFAULT_NAME = 'plug_name'


    def parser(self, req):
        """
        Parsing the request from client.

        Args:
            req: byte array request from client.

        Returns:
            None: unknown format of request.

            [self.OP_REFRESH]: operation refresh

            [self.OP_CONTROL, house, code, status]:
                operation control
                house: string composed of 0 and 1, length 5
                code: string composed of 0 and 1, length 5
                status: string 'on' or 'off'

            [self.OP_DELETE, house, code]:
                operation delete
                house: string composed of 0 and 1, length 5
                code: string composed of 0 and 1, length 5

            [self.OP_ADD, house, code, name, status]:
                operation add
                house: string composed of 0 and 1, length 5
                code: string composed of 0 and 1, length 5
                name: string with max. length 16
                status: string 'on' or 'off'
        """

        if not self.PROTO_MIN_LEN <= len(req) <= self.PROTO_MAX_LEN:
            return None

        int_format = int.from_bytes(req[:self.PROTO_MIN_LEN], 'big')

        # Getting request type
        req_type = int_format >> (self.PROTO_BIT_LEN - self.PROTO_TYPE_BIT_LEN)

        if req_type == self.OP_REFRESH and int_format & 0x01:
            return [self.OP_REG]

        # Getting plug's identifier
        plug_id = int_format \
            & (~(0x03 << self.PROTO_BIT_LEN - self.PROTO_TYPE_BIT_LEN))
        plug_id = plug_id \
            >> (self.PROTO_STATUS_BIT_LEN + self.PROTO_RESV_BIT_LEN)
        plug_id = bin(plug_id)[2:]
        zeros = self.PROTO_HOUSE_BIT_LEN + self.PROTO_CODE_BIT_LEN \
            - len(plug_id)
        plug_id = '0' * zeros + plug_id

        house = plug_id[:self.PROTO_HOUSE_BIT_LEN]
        code = plug_id[self.PROTO_HOUSE_BIT_LEN:]

        status = 'off'
        name_len = 0
        name = self.PLUG_DEFAULT_NAME

        # Getting status if the type is not adding new plug
        if req_type != self.OP_ADD:
            status = int_format & 0x0F
            status >>= self.PROTO_RESV_BIT_LEN
            status = 'on' if status == 2 else 'off'
        else:
            name_len = int_format & 0x0F

        if len(req) - self.PROTO_MIN_LEN != name_len:
            return None
        else:
            name = req[self.PROTO_MIN_LEN:].decode()

        if req_type == self.OP_REFRESH:
            return [self.OP_REFRESH]
        elif req_type == self.OP_CONTROL:
            return [self.OP_CONTROL, house, code, status]
        elif req_type == self.OP_DELETE:
            return [self.OP_DELETE, house, code]
        elif req_type == self.OP_ADD:
            return [self.OP_ADD, house, code, name, status]
        else:
            return None
