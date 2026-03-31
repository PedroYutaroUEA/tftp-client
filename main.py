from src.app import App
from src.view import TFTPViewer

if __name__ == "__main__":
    app = App()
    tftp_viwer = TFTPViewer()

    app.exec_sys(viwer=tftp_viwer)
