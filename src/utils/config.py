import os


class AppConfig:
    """
    App state settings manager
    """

    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 6969
        self.download_path = os.path.abspath("downloads")
        self.upload_path = os.path.abspath("upload")
        self.block_size = 512
        self.timeout = 5

    def update_network(self, host, port):
        self.host = host
        self.port = port

    def update_conn_params(self, block_size: int, timeout: int):
        self.block_size = block_size
        self.timeout = timeout

    def update_paths(self, download_path: str, upload_path: str):
        self.download_path = os.path.abspath(download_path)
        self.upload_path = os.path.abspath(upload_path)
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.upload_path, exist_ok=True)
