#!/usr/bin/env python3
# Communication Systems Lab
# Assignment 3
# Task 3.2
# Author: Tong, Michael
# ##############################
# Description:
# Sensor Network Server
#

# Asynchronous IO support
import asyncio
import sys

# Daemonizing server
from daemon_process import DaemonProcess

# Sensor Network Protocol
from sns_proto import SensorNetProtocol


class SensorNetServer(DaemonProcess):
    """
    Sensor Network Server.
    """

    def __init__(self, pid_file, port=8123):
        """
        Initialization.

        Args:
            pid_file: The file name for storing daemon process PID.
            port: The server's port, 8123 by default.
        """

        # Initializing parent class
        super(SensorNetServer, self).__init__(pid_file)

        # Initializing event loop
        self.event_loop = asyncio.get_event_loop()

        # Server setting
        self.host = '0.0.0.0' # Please firstly check ifconfig
        self.port = port

        self.server = self.event_loop.create_datagram_endpoint(
            SensorNetProtocol, local_addr=(self.host, self.port))


    def run(self):
        """
        Overriding the run function in parent class.
        The event loop begins from here.
        """

        # Generating asynchronous server object
        self.event_loop.run_until_complete(self.server)

        # Main event loop begins to work
        self.event_loop.run_forever()


if __name__ == '__main__':
    # Checking python version
    if sys.version_info < (3, 5, 0):
        print('Must use Python 3.5.0 or later.')
        exit(1)

    # Entrance, creating server object
    daemon = SensorNetServer('/var/mysns/csl_sns_daemon.pid')

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
