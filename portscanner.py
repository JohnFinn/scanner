#!/usr/bin/env python
import socket
from select import select
from time import time
import asyncio


# TODO maybe there is a way to get port, a socket is trying to connect to and if there is, it won't be neccessary to store ports in dict
async def scan(addresses):
    sockets = {}
    for address in addresses:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        sockets[sock] = address
        sock.connect_ex(address)
    while sockets:
        await asyncio.sleep(0)
        _, done, _ = select([],sockets.keys(),[],0)
        for sock in done:
            address = sockets[sock]
            del sockets[sock]
            yield address, sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0
    # I've found out that sockets will close implicitly, but don't know what about async functions

async def open_ports(ports):
    async for address, is_open in scan(ports):
        if is_open:
            yield address

async def main():
    async for address in open_ports(map(lambda port: ('scanme.nmap.org', port), range(300))):
        print(address)

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
