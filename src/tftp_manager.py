import os
from tftpy.TftpPacketTypes import TftpPacketDAT, TftpPacketACK
import logging
import tftpy

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TFTPManager:
    """
    Encapsula a lógica da RFC 1350 usando a lib tftpy.
    """

    def __init__(self, connection, base_path="."):
        self.conn = connection
        self.base_path = os.path.abspath(base_path)
        self.client = tftpy.TftpClient(self.conn.host, self.conn.port)

        os.makedirs(self.base_path, exist_ok=True)

    def set_base_path(self, new_path: str):
        self.base_path = os.path.abspath(new_path)
        os.makedirs(self.base_path, exist_ok=True)
        return self.base_path

    def progress_callback(self, pkt):
        """Callback para visualização de pacotes em tempo real."""

        if isinstance(pkt, TftpPacketDAT):
            print(f"  [RECV] Bloco #{pkt.blocknr} - {len(pkt.data)} bytes recebidos")
        elif isinstance(pkt, TftpPacketACK):
            print(f"  [SENT] ACK Bloco #{pkt.blocknr}")

    def list_local_files(self):
        return os.listdir(self.base_path)

    def download(self, remote_file, local_file):
        """Abstração do Opcode 1 (RRQ)"""
        target_path = os.path.join(self.base_path, local_file)
        print(f"Iniciando download de '{remote_file}' para '{target_path}'...")
        try:
            print(f"Conectando em {self.conn.host}:{self.conn.port}...")
            self.client.download(
                filename=remote_file,
                output=local_file,
                packethook=self.progress_callback,
            )
            return True, f"Sucesso: '{remote_file}' baixado como '{local_file}'."
        except Exception as e:
            return False, f"Erro no Download: {e}"

    def upload(self, remote_file, local_file):
        """Abstração do Opcode 2 (WRQ)"""
        source_path = os.path.join(self.base_path, local_file)
        if not os.path.exists(source_path):
            return False, f"Erro: Arquivo local '{local_file}' não encontrado."

        print(f"Iniciando upload de '{source_path}' para o servidor...")
        try:
            print(f"Conectando em {self.conn.host}:{self.conn.port}...")
            self.client.upload(
                filename=remote_file,
                input=local_file,
                packethook=self.progress_callback,
            )
            return (
                True,
                f"Sucesso: '{local_file}' enviado como '{remote_file}'.",
            )
        except Exception as e:
            return False, f"Erro no Upload: {e}"
