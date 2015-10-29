#
# Communication Systems Lab
# Assignment 2
# Task 2.2
# Author: Tong, Michael
# ##############################
# Description:
#

# Asynchronous IO support
import asyncio

from daemon_process import DaemonProcess


class CompressProxyServer(DaemonProcess):
    '''
    pass
    '''

    def __init__(self):
        '''
        pass
        '''

        self.pid_file = 'csl_proxy_server_daemon.pid'
        super(CompressProxyServer, self).__init__(self.pid_file)


        self.event_loop = asyncio.get_event_loop()

        pass

    def run(self):
        '''
        Overriding
        '''

        self.event_loop.run_forever()


if __name__ == '__main__':
    # Entrance, creating server object
    daemon = CompressProxyServer()

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
