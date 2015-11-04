#!/usr/bin/env python3
# Communication Systems Lab
# Assignment 2
# Task 2.2
# Author: Tong, Michael
# ##############################
# Description:
#

# Asynchronous IO support
import asyncio
import sys
# HTTP content compression
import gzip
import urllib.parse

# Memory cache support
import hashlib
from datetime import datetime, timedelta
import copy

# Daemonizing server
from daemon_process import DaemonProcess


class AsynCompressProxy(DaemonProcess):
    '''
    HTTP Proxy with compression function, implemented in Asynchronous IO.

    Args:
        port: The port to bind.
    '''

    def __init__(self, port=8123):
        '''
        Initialization.
        '''

        # Initializing parent class
        self.pid_file = '/var/myproxy/csl_proxy_server_daemon.pid'
        super(AsynCompressProxy, self).__init__(self.pid_file)

        # Initializing main event loop
        self.event_loop = asyncio.get_event_loop()

        # Buffer size
        self.read_buf_size = 655360

        # Initializing server coroutine
        self.host = ''
        self.port = port

        self.server_coro = asyncio.start_server(self._req_handler,
                                           self.host, self.port,
                                           loop = self.event_loop)

        self.hash_tool = hashlib.md5
        self.mem_cached = dict()
        self.cache_live = timedelta(0, 3600, 0)


    async def _req_handler(self, reader, writer):
        """
        Coroutine: Handling the HTTP request.

        Args:
            reader:
                StreamReader object, utilized to read request from client.
            writer:
                StreamWriter object, utilized to write response to client.
        """

        # Reading raw request data from reader (type SreamReader)
        req_raw = await reader.readline()
        req_content = req_raw.decode()

        # Getting target address
        target = req_content.split(' ')[1]

        # Getting compressed response
        resp = await self._get_response(target)

        # Responsing
        writer.write(resp)
        await writer.drain()

        writer.close()


    async def _get_response(self, target):
        """
        Getting response. From memory or from web server.

        Args:
            target: The target address.

        Returns:
            The response is a tuple in form of (resp_hdr, resp_cont)
        """

        # Checking if record already exists, if not, requesting from web server
        resp = self._get_mem_cache(target)

        if resp is None:
            resp = await self._get_remote(target)
            resp = self._compress_resp(resp)
            self._add_mem_cache(target, resp)

        return resp


    def _get_mem_cache(self, target):
        """
        Getting response from cached data in memory.

        Args:
            target: The target address.

        Returns:
            The response is a tuple in form of (resp_hdr, resp_cont)
        """

        key = self._calc_hash(target)
        if key not in self.mem_cached \
                or self.mem_cached[key]['last'] \
                + self.cache_live < datetime.now():
            return None
        else:
            return self.mem_cached[key]['content']


    def _add_mem_cache(self, target, value):
        """
        Adding new record into memory cache.

        Args:
            target: The target address.
            value: The compressed data.
        """

        key = self._calc_hash(target)
        self.mem_cached[key] = dict()
        self.mem_cached[key]['last'] = datetime.now()
        self.mem_cached[key]['content'] = copy.deepcopy(value)


    def _calc_hash(self, target):
        """
        Calculating hash of input address.

        Args:
            target: The target address.
        """

        return self.hash_tool(target.encode()).hexdigest()


    async def _get_remote(self, target):
        """
        Getting response from web server.

        Args:
            target: The target address.

        Returns:
            The response is a tuple in form of (resp_hdr, resp_cont)
        """

        # Parsing url into different parts
        url = urllib.parse.urlsplit(target)

        # Setting up connection according to protocol type
        conn = asyncio.open_connection(url.hostname, 443, ssl=True) \
            if url.scheme == 'https' else \
            asyncio.open_connection(url.hostname, 80)
        reader, writer = await conn

        # Assembling request header
        req = ('GET {path} HTTP/1.0\r\n'
               'Host: {hostname} \r\n'
               '\r\n').format(path = url.path or '/', hostname = url.hostname)

        # Sending request
        writer.write(req.encode('utf-8'))

        # Reading response
        resp_hdr = ''
        resp_cont = ''
        content_flag = False

        while True:
            line = await reader.readline()
            if not line:
                break
            else:
                if content_flag:
                    resp_cont += line.decode('utf-8').rstrip()
                else:
                    if line.decode('utf-8') \
                            == '<?xml version="1.0" encoding="utf-8"?>\n':
                        content_flag = True
                        resp_cont += line.decode('utf-8').rstrip()
                    else:
                        resp_hdr += line.decode('utf-8')

        return (resp_hdr, resp_cont)


    def _compress_resp(self, resp):
        """
        Compressing the response content.

        Args:
            resp:
                The response, it is a tuple in form of (resp_hdr, resp_cont),
                where resp_hdr is the response header, and resp_cont is the
                response content.

        Returns:
            A combined response, including modified header and
            compressed content.
        """

        print('Header Before: %d' % len(resp[0]))
        print('Content Before: %d' % len(resp[1]))
        # Compressing content and get the compressed size
        c_resp_cont = gzip.compress(resp[1].encode('utf-8'))
        c_resp_cont_len = len(c_resp_cont)

        # Modifying response header
        new_resp_hdr = resp[0].split('\r\n')
        content_encoding_flag = True
        encoding_field = 'Content-Encoding: gzip'

        for idx in range(len(new_resp_hdr)):
            item = new_resp_hdr[idx]
            if item.startswith('Content-Length: '):
                new_resp_hdr[idx] = 'Content-Length: %d' % c_resp_cont_len
            elif item.startswith('Content-Encoding: '):
                content_encoding_flag = False
                new_resp_hdr[idx] = encoding_field
            else:
                continue

        if content_encoding_flag:
            new_resp_hdr.insert(-3, encoding_field)

        # Joining the header and the content.
        new_resp_hdr = '\r\n'.join(new_resp_hdr)
        print('Header Length: %d' % len(new_resp_hdr))
        print('Content Length: %d' % c_resp_cont_len)

        return b''.join([new_resp_hdr.encode('utf-8'), c_resp_cont])


    def run(self):
        '''
        Overriding the run function in parent class.
        The event loop begins from here.
        '''

        # Generating asynchronous server object
        self.event_loop.run_until_complete(self.server_coro)

        # Main event loop begins to work
        self.event_loop.run_forever()


if __name__ == '__main__':
    # Checking python version
    if sys.version_info < (3, 5, 0):
        print('Must use Python 3.5.0 or later.')
        exit(1)


    # Entrance, creating server object
    daemon = AsynCompressProxy()


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
