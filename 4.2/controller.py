#!/usr/bin/env python3
# Communication Systems Lab
# Assignment 4
# Task 4.3
# Author: Tong, Michael
# ##############################
# Description:
# Controller for communicating with Raspberry PI
#

import asyncio
import sys
import os

# Daemonizing server
from daemon_process import DaemonProcess


class Controller(DaemonProcess):
    """
    Plug switch controller.
    """

    def __init__(self, server_addr, controller_path, pid_file):
        """
        Initialization.

        Args:
            server_addr: The server's address and port
            controller_path: The controller file path
            pid_file: The pid file for daemonization
        """

        # Initializing parent class
        super(Controller, self).__init__(pid_file)

        # Server
        self.server_addr = server_addr
        self.reg_data = b'\x00\x01'

        # Controller program
        self.controller = controller_path

        # Initializing main event loop and server
        self.event_loop = asyncio.get_event_loop()


    def run(self):
        """
        Overriding the run function in parent class.
        The event loop begins from here.
        """

        # Generating asynchronous server object
        self.event_loop.run_until_complete(self.reg())

        # Main event loop begins to work
        self.event_loop.run_forever()


    async def reg(self):
        """
        Coroutine: The controller for communicating with server
        """

        self.reader, self.writer = await asyncio.open_connection(
            self.server_addr[0], self.server_addr[1], loop=self.event_loop)

        self.writer.write(self.reg_data)

        while (True):
            req = await self.reader.read(16)
            req = req.decode()

            house = req[:5]
            code = req[5:10]
            status = req[11:]

            command = '%s -h %s -c %s -s %s -l %s' % (self.controller, house,
                                                      code, status, '168')
            os.system(command)


if __name__ == '__main__':
    # Checking python version
    if sys.version_info < (3, 5, 0):
        exit(1)

    # Entrance, creating server object
    daemon = Controller(('cslectures.tongsucn.com', 8233),
                        './controller', 'controller.pid')

    # Parsing arguments
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print('Usage: %s [start|stop|restart]' % sys.argv[0])
            sys.exit(1)
    else:
        print('Usage: %s [start|stop|restart]' % sys.argv[0])
        sys.exit(1)
