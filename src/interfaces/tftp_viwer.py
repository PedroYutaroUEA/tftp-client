from abc import ABC, abstractmethod


class ITFTPViwer(ABC):
    """
    Abstração do Viwer
    """

    @abstractmethod
    async def run(self) -> None:
        """
        Main execution method
        """
