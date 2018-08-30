#!/usr/bin/env python
import socket, select, errno
import asyncio

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

async def check_port(addr):
    s = Socket(socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
    try:
        await s.connect_async(addr)
    except ConnectionRefusedError:
        return False
    else:
        return True
    finally:
        s.close()

async def print_port(port):
    if await check_port(('scanme.nmap.org', port)):
        print('[+]', port)
    else:
        print('[-]', port)

# for port in range(65536):
#     s = socket.socket()
#     try:
#         s.connect(('scanme.nmap.org', port))
#     except ConnectionRefusedError:
#         print('[-]', port)
#     else:
#         print('[+]', port)
#     finally:
#         s.close()

loop = asyncio.get_event_loop()
tasks = asyncio.gather(*map(print_port, range(1024)))
loop.run_until_complete(tasks)

# for port in range(65536):
#     s = Socket(socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
#     loop.create_task()
# cr = s.connect_async(('scanme.nmap.org', 80))
# loop.run_until_complete(cr)
# s.close()
