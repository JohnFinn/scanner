#!/usr/bin/env python
import socket
from select import select
from time import time

class Scanner:

    def __init__(self, host):
        self.host = host

    # TODO make nonblocking by yielding at each iteration in while loop
    def scan(self, ports, timeout=10):
        sockets = {}
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
            sockets[sock] = port
            sock.connect_ex((self.host, port))
        time_point = time() + timeout
        while sockets and time() < time_point:
            _, done, _ = select([],sockets.keys(),[],0)
            for sock in done:
                port = sockets[sock]
                del sockets[sock]
                yield port, sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0

    def open_ports(self, ports):
        for port, is_open in self.scan(ports):
            if is_open:
                yield port
        # return map(operator.itemgetter(0), filter(operator.itemgetter(1), ports))

if __name__ == '__main__':
    scanner = Scanner('scanme.nmap.org')
    for port in scanner.open_ports(range(300)):
        print(port)
    # for port, is_open in scanner.scan(range(1024), 3):
    #     if is_open:
    #         print('[+]', port)
    #     else:
    #         print('[-]', port)
# print('=============')
# for port in range(30):
#     s = socket.socket()
#     try:
#         s.connect(('scanme.nmap.org', port))
#     except ConnectionRefusedError:
#         print('[-]', port)
#     else:
#         print('[+]', port)
#     finally:
#         s.close()
