import socket


class UDPConnection:
    """
    Abstração do Socket UDP. lida puramente com o envio e recebimento de bytes via UDP.
    """

    def __init__(self, host: str, port: int = 69):
        self.host = host
        self.port = port

    def validate_host(self, host):
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
            print(f"Erro: Host {host} inválido ou inacessível.")
            return host

    def __str__(self):
        return f"{self.host}:{self.port}"
