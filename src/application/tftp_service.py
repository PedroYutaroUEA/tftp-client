from src.utils import FileSystemHandler
from src.interfaces import ITFTPService


class TFTPService(ITFTPService):
    """
    Classe Wrapper do cliente TFTP - Abstrai Operações
    """

    def __init__(self, engine, config):
        self.engine = engine
        self.config = config
        self.fs = FileSystemHandler()
        self.fs.ensure_dir(self.config.download_path)
        self.fs.ensure_dir(self.config.upload_path)

    def list_local_files(self) -> dict:
        """
        Lista arquivos locais
        """
        downloads = self.fs.list_dir(self.config.download_path)
        uploads = self.fs.list_dir(self.config.upload_path)

        return {"downloads": downloads, "uploads": uploads}

    async def download(self, filename: str, overwrite=False) -> tuple[bool, str]:
        exists = self.fs.file_exists(self.config.download_path, filename)
        if exists and not overwrite:
            return False, "Arquivo já existe localmente."

        print(f"[LOG] Iniciando fluxo RRQ para: {filename}")
        try:
            with self.fs.get_write_handle(self.config.download_path, filename) as f:
                # Passamos o f.write como o callback de consumo de dados
                await self.engine.read_file(filename, f.write)
            return (
                True,
                f"Download concluído com sucesso em {self.config.download_path}",
            )
        except Exception as e:
            return False, f"Falha no download: {e}"

    async def upload(self, filename: str) -> tuple[bool, str]:
        if not self.fs.file_exists(self.config.upload_path, filename):
            return False, "Arquivo não encontrado na pasta de upload."

        print(f"[LOG] Iniciando fluxo WRQ para: {filename}")
        try:
            with self.fs.get_read_handle(self.config.upload_path, filename) as f:
                # Passamos uma função lambda que lê blocos do arquivo
                await self.engine.write_file(filename, f.read)
            return True, "Upload concluído com sucesso."
        except Exception as e:
            return False, f"Falha no upload: {e}"
