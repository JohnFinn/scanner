#!/usr/bin/env python
import socket
from select import select
from time import time
import asyncio

class Scanner:

    def __init__(self, host):
        self.host = host

    # TODO maybe there is a way to get port, a socket is trying to connect to and if there is, it won't be neccessary to store ports in dict
    async def scan(self, ports):
        sockets = {}
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
            sockets[sock] = port
            sock.connect_ex((self.host, port))
        while sockets:
            await asyncio.sleep(0)
            _, done, _ = select([],sockets.keys(),[],0)
            for sock in done:
                port = sockets[sock]
                del sockets[sock]
                yield port, sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0
        # I've found out that sockets will close implicitly, but don't know what about async functions

    async def open_ports(self, ports):
        async for port, is_open in self.scan(ports):
            if is_open:
                yield port

async def main():
    scanner = Scanner('scanme.nmap.org')
    async for port in scanner.open_ports(range(300)):
        print(port)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
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
