import questionary
from . import TFTPClient
from enum import Enum


class OPT(Enum):
    DOWNLOAD = "Download (GET)"
    UPLOAD = "Upload (PUT)"
    EXIT = "Sair"


def run_cli():
    client = TFTPClient(server_ip="127.0.0.1")

    choices = [opt.value for opt in OPT]

    action = questionary.select(
        "TFTP Client - Selecione a operação:",
        choices=choices,
    ).ask()

    if action == OPT.DOWNLOAD.value:
        filename = questionary.text("Nome do arquivo remoto:").ask()
        client.download(filename)
