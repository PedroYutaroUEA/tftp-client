import socket
import asyncio


class AsyncUDPConnection:
    """
    async TFTP Connection manager
    """

    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def open(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        return self.sock

    async def send(self, data, addr=None):
        loop = asyncio.get_running_loop()
        target = addr if addr else (self.host, self.port)
        await loop.sock_sendto(self.sock, data, target)

    async def receive(self, buffer=1024):
        loop = asyncio.get_running_loop()
        # Implementa um timeout básico para o recv
        data, addr = await asyncio.wait_for(
            loop.sock_recvfrom(self.sock, buffer), timeout=self.timeout
        )
        return data, addr
