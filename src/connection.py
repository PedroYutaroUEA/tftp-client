import socket


class UDPConn:
    """
    Abstração do Socket UDP. lida puramente com o envio e recebimento de bytes via UDP.
    """

    def __init__(self, host, port=69, timeout=5):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

    def send(self, data, address):
        """Método de envio de dados a um determinado host"""
        addr = address if address else (self.host, self.port)
        self.sock.sendto(data, addr)

    def receive(self, buffer_size=1024):
        """Método de recebimento de bytes, dado um buffer size"""
        try:
            data, addr = self.sock.recvfrom(buffer_size)
            return data, addr
        except socket.timeout:
            return None, None
