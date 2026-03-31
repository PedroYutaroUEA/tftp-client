import os


class FileSystemHandler:
    @staticmethod
    def ensure_dir(path: str):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def list_dir(path: str):
        if not os.path.exists(path):
            return []
        return os.listdir(path)

    @staticmethod
    def file_exists(directory, filename: str):
        return os.path.exists(os.path.join(directory, filename))

    @staticmethod
    def get_write_handle(directory, filename: str):
        return open(os.path.join(directory, filename), "wb")

    @staticmethod
    def get_read_handle(directory, filename: str):
        return open(os.path.join(directory, filename), "rb")
