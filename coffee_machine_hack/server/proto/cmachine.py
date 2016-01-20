#!/usr/bin/env python3


import time
import logging

from coffee_cmd import CoffeeCommand as CC
from coffee_proto import CoffeeMachine as CM


class CoffeeMachine(object):
    """
    Coffee machine instance
    """

    def __init__(self, addr, port):
        """
        Initializing coffee machine setting.

        Args:
            addr: Address of the coffee machine.
            port: The port that the machine uses.
        """

        # Variables about the coffee machine
        self.status = False
        self.machine = CM(addr, port)
        self.product_list = None

        # Initializing logging
        logging.basicConfig(filename='./%d.log' % int(time.time()),
                            format='%(asctime)s %(message)s',
                            level=logging.DEBUG)

        # Setting up connection with the coffee machine
        # Need exception handle here
        self.machine.conn()


    def _req_product_list(self):
        """
        Send request for product list.
        """

        if self.status:
            resp = self.machine.control(CC.REQ_LIST)
            lst = list(filter(lambda x : len(x) > 0, resp.split(';')))
            self.product_list = list(enumerate(lst), start=1)


    def turn_on(self):
        """
        Turn on the coffee machine. Flag status will be set to True after
        calling.
        """

        # Need to handle the response
        resp = self.machine.control(CC.TURN_ON)
        self.status = True

        # Require product list
        self._req_product_list()


    def turn_off(self):
        """
        Turn off the coffee machine. Flag status will be set to False after
        calling.
        """

        if self.status:
            self.machine.control(CC.TURN_OFF)
            self.machine.disconn()
            self.status = False


    def flushing(self):
        """
        Flushing the coffee machine.
        """

        if self.status:
            resp = self.machine.control(CC.FLUSHING)


    def product_list(self):
        """
        Provide the list of products.

        Returns:
            Product lists that the coffee machine provides. In format:
                [(1, 'Product 1'), (2, 'Product 2'), ...]
        """
        return self.product_list


    def make_product(self, product):
        """
        Make a specified product.

        Args:
            product: The product specification, in tuple format:
                (id, name)
                id: int, the product's ID, range [1, 7]
                name: str, the product's name
        """

        if self.status and 0 < product[0] < 8:
            resp = self.machine.control(PRODUCT[product[0] - 1])

            return True
        else:
            return False


    def is_on(self):
        """
        Return the status of coffee machine.

        Returns:
            True: The coffee machine is on.
            False: The coffee machine is off.
        """
        return self.status


    def has_water(self):
        """"""
        pass


    def has_bean(self):
        """"""
        pass


    def has_creme(self):
        """"""
        pass
