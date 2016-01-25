#!/usr/bin/env python3

import socket
import coffee_pb2

if __name__ == '__main__':
    cmd = coffee_pb2.CoffeeCommand()
    cmd.type = coffee_pb2.CoffeeCommand.OPERATION
    cmd.command = b'AN:01'

    resp = coffee_pb2.Response()

    msg = cmd.SerializeToString()

    # UDP
    addr = '192.168.199.233'
    port = 8233

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    print('Message length: %d, message content: %s' % (len(msg), msg))
    sock.sendto(msg, (addr, port))

    (recv_msg, (remote_addr, remote_port)) = sock.recvfrom(1024)
    resp.ParseFromString(recv_msg)
    print('Receive from %s:%d' % (remote_addr, remote_port))
    print('Response type: %d' % (resp.type))
    print('Response description: %s' % (resp.description))
