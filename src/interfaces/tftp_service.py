from abc import ABC, abstractmethod


class ITFTPService(ABC):
    """
    Abstração do Service de TFTP
    """

    @abstractmethod
    async def download(self, filename: str, overwrite=False) -> tuple[bool, str]:
        """
        Realiza operação de WRQ | client <--- server
        """

    @abstractmethod
    async def upload(self, filename: str) -> tuple[bool, str]:
        """
        Realiza operação de RRQ | client ---> server
        """
