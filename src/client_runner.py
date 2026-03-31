import os
import argparse
from enum import Enum

import questionary
from . import TFTPManager, UDPConnection


class OPT(Enum):
    DOWNLOAD = "Download (GET)"
    UPLOAD = "Upload (PUT)"
    LIST_LOCAL = "Listar Arquivos Locais"
    CHANGE_LOCAL_REPO = "Alterar Pasta de Armazenamento"
    EXIT = "Sair"


def get_conn():
    parser = argparse.ArgumentParser(description="UEA-EST TFTP Client")
    parser.add_argument("--host", help="IP do Servidor TFTP")
    parser.add_argument("--port", type=int, default=69, help="Porta (padrão 69)")
    args = parser.parse_args()

    host = args.host or questionary.text("Qual o IP do servidor?").ask()
    port = args.port or int(questionary.text("Qual a porta?", default="69").ask())

    if not host:
        print("Erro: Host não definido.")
        exit(1)

    return UDPConnection(host, port)


def run_cli():
    conn = get_conn()
    client = TFTPManager(connection=conn, base_path="./repository")

    print(f"\nConectado a: {conn}")

    choices = [opt.value for opt in OPT]

    while True:
        print(f"\n[Status] Servidor: {conn} | Pasta Local: {client.base_path}")

        op = questionary.select(
            "TFTP Client - Selecione a operação:",
            choices=choices,
        ).ask()

        if op == OPT.EXIT.value:
            print("Saindo...")
            break

        if op == OPT.DOWNLOAD.value:
            remote = questionary.text("Nome do arquivo remoto:").ask()
            local = questionary.text("Nome do arquivo local:").ask()
            success, msg = client.download(remote_file=remote, local_file=local)
            print(f"Status: {'Sucesso' if success else 'Falha'}.\n Mensagem: {msg}.\n")

        elif op == OPT.UPLOAD.value:
            local = questionary.text("Caminho do arquivo local:").ask()
            remote = questionary.text(
                "Nome no servidor:", default=os.path.basename(local)
            ).ask()
            success, msg = client.upload(remote, local)
            print(f"Status: {'Sucesso' if success else 'Falha'}.\n Mensagem: {msg}.\n")

        elif op == OPT.LIST_LOCAL.value:
            files = client.list_local_files()
            print("\n--- Arquivos na pasta local ---")
            for f in files:
                print(f" - {f}")

        elif op == OPT.CHANGE_LOCAL_REPO.value:
            new_path = questionary.text("Novo caminho (ex: ./meus_arquivos):").ask()
            actual = client.set_base_path(new_path)
            print(f"Pasta alterada para: {actual}")
