#!/usr/bin/env python
import socket, select, errno
import asyncio, itertools
from queue import Queue

class Socket(socket.socket):
    async def connect_async(self, address):
        self.connect_ex(address)
        while True:
            await asyncio.sleep(0)
            r,w,x = select.select([], [self], [self], 0) # TODO find out what x does
            if w:
                err = self.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err == 0:
                    return
                elif err == errno.ECONNREFUSED:
                    raise ConnectionRefusedError
                else:
                    raise ConnectionError(err)


class Scanner:

    def __init__(self, host):
        self.host = host
        self._ports = Queue()

    async def check_port(self, port:int):
        s = Socket(socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        try:
            await s.connect_async((self.host, port))
        except ConnectionRefusedError:
            return False
        else:
            return True
        finally:
            s.close()

    async def put_port(self, port:int):
        self._ports.put((port, await self.check_port(port)))
    # TODO yeild completed tasks before everyone else is complete
    def scan(self, ports):
        ports1, ports2 = itertools.tee(ports) # in order to know how many times we need to call get
        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*map(self.put_port, ports1))
        loop.run_until_complete(tasks)
        for port in ports2:
            yield self._ports.get()

scanner = Scanner('scanme.nmap.org')
for port, is_open in scanner.scan(range(20,25)):
    if is_open:
        print('[+]', port)
    else:
        print('[-]', port)

for port in range(20,25):
    s = socket.socket()
    try:
        s.connect(('scanme.nmap.org', port))
    except ConnectionRefusedError:
        print('[-]', port)
    else:
        print('[+]', port)
    finally:
        s.close()
