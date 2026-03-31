from enum import Enum
from colorama import Fore, init
import questionary

# Importações das suas camadas (Componentes C4)
from src.utils import AppConfig, FileSystemHandler
from src.core.infra import AsyncUDPConnection
from src.core.domain import TFTPEngine
from src.application import TFTPService
from src.interfaces import ITFTPViwer


class OPTIONS(Enum):
    """
    Opções do client
    """

    LIST_LOCAL = "Listar Arquivos (Locais)"
    DOWNLOAD = "Baixar Arquivo (RRQ)"
    UPLOAD = "Enviar Arquivo (WRQ)"
    SETTINGS = "Configurações do Sistema"
    EXIT = "Sair"


# Inicializa colorama para logs coloridos no terminal/kitty
init(autoreset=True)


class TFTPViewer(ITFTPViwer):
    """
    Classe principalde execução
    """

    def __init__(self):
        # 1. Configuração inicial (Provider)
        self.config = AppConfig()
        # 2. Infraestrutura
        self.conn = AsyncUDPConnection(self.config.host, self.config.port, timeout=10)
        # 3. Core do Protocolo (Engine manual RFC 1350)
        self.engine = TFTPEngine(
            connection=self.conn, block_size=self.config.block_size
        )
        # 4. Camada de Aplicação (Service)
        self.service = TFTPService(engine=self.engine, config=self.config)

    def display_status(self):
        """Exibe um 'dashboard' rápido das configurações atuais."""
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}TFTP CLIENT - STATUS")
        print(
            f"{Fore.WHITE}Servidor: {Fore.GREEN}{self.config.host}:{self.config.port}"
        )
        print(f"{Fore.WHITE}Pasta Download: {Fore.BLUE}{self.config.download_path}")
        print(f"{Fore.WHITE}Pasta Upload:   {Fore.BLUE}{self.config.upload_path}")
        print(f"{Fore.CYAN}{'='*50}\n")

    async def change_settings(self):
        """Menu para alteração dinâmica de configurações."""
        new_host = await questionary.text(
            "Novo IP do Servidor:", default=self.config.host
        ).ask_async()
        new_port = await questionary.text(
            "Nova Porta:", default=str(self.config.port)
        ).ask_async()
        new_dl = await questionary.text(
            "Nova pasta de Download:", default=self.config.download_path
        ).ask_async()
        new_up = await questionary.text(
            "Nova pasta de Upload:", default=self.config.upload_path
        ).ask_async()
        save = str(input("Salvar Alterações [y/n]: "))
        if save.lower() in ("n"):
            print("Descartando alterações...")
            return

        self.config.update_network(new_host, int(new_port))
        self.config.update_paths(new_dl, new_up)

        # Re-inicializa a conexão com os novos dados
        self.conn.host = self.config.host
        self.conn.port = self.config.port
        print(f"{Fore.GREEN}Configurações atualizadas!")

    async def run(self):
        """Loop principal da interface."""
        choices = [op.value for op in OPTIONS]
        while True:
            self.display_status()

            option = await questionary.select(
                "Selecione uma operação:",
                choices=choices,
            ).ask_async()

            if option == OPTIONS.EXIT.value:
                print(f"{Fore.RED}Encerrando aplicação...")
                break

            elif option == OPTIONS.SETTINGS.value:
                await self.change_settings()

            elif option == OPTIONS.LIST_LOCAL.value:
                files = self.service.list_local_files()
                print(f"\n{Fore.YELLOW}[DOWNLOADS]: {Fore.WHITE}{files['downloads']}")
                print(f"{Fore.YELLOW}[UPLOADS]:   {Fore.WHITE}{files['uploads']}")

            elif option == OPTIONS.DOWNLOAD.value:
                filename = await questionary.text(
                    "Nome do arquivo no servidor:"
                ).ask_async()

                # Lógica de sobrescrita gerenciada pelo Viewer
                overwrite = False
                if FileSystemHandler.file_exists(self.config.download_path, filename):
                    overwrite = await questionary.confirm(
                        "Arquivo já existe. Sobrescrever?"
                    ).ask_async()
                    if not overwrite:
                        continue

                success, msg = await self.service.download(filename, overwrite=True)
                print(f"{Fore.GREEN if success else Fore.RED}{msg}")

            elif option == OPTIONS.UPLOAD.value:
                filename = await questionary.text(
                    "Nome do arquivo na pasta de upload:"
                ).ask_async()
                success, msg = await self.service.upload(filename)
                print(f"{Fore.GREEN if success else Fore.RED}{msg}")
