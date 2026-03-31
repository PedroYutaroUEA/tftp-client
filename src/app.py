import sys
import asyncio
from src.interfaces import ITFTPViwer


class App:
    """
    main exec function
    """

    def exec_sys(self, viwer: ITFTPViwer):
        """
        app exec method
        """
        try:
            asyncio.run(viwer.run())
        except KeyboardInterrupt:
            print("\nInterrupção detectada. Saindo...")
            sys.exit(0)
