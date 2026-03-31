import asyncio
import socket
import argparse
import os
import struct
from protocol.packet import TFTPPacket

class TFTPClient:
    def __init__(self, host, port=6969, block_size=512):
        self.host = host
        self.port = port
        self.block_size = block_size

    async def get(self, filename):
        """Baixa um arquivo do servidor (RRQ)"""
        # Opcode 1 (RRQ) + filename + 0 + mode (octet) + 0
        request = b'\x00\x01' + filename.encode() + b'\x00octet\x00'
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        loop = asyncio.get_running_loop()

        await loop.sock_sendto(sock, request, (self.host, self.port))
        
        expected_block = 1
        print(f"Baixando {filename}...")

        with open(f"downloads/{filename}", 'wb') as f:
            while True:
                data, addr = await loop.sock_recvfrom(sock, self.block_size + 4)
                packet = TFTPPacket.parse(data)

                if packet['opcode'] == 3:  # DATA
                    # No seu packet.py, o bloco é extraído no parse
                    block_num = struct.unpack('!H', data[2:4])[0]
                    if block_num == expected_block:
                        # O conteúdo do dado começa após os 4 bytes de cabeçalho
                        f.write(data[4:])
                        ack_packet = TFTPPacket.ack(block_num)
                        await loop.sock_sendto(sock, ack_packet, addr)
                        expected_block += 1
                    
                    if len(data[4:]) < self.block_size:
                        print("Download concluído com sucesso.")
                        break
                elif packet['opcode'] == 5: # ERROR
                    print(f"Erro: {data[4:-1].decode()}")
                    break

    async def put(self, filename):
        """Envia um arquivo da pasta 'upload' para o servidor"""
        # Define o caminho para a pasta upload
        upload_dir = "upload"
        
        # Constrói o caminho completo do arquivo
        file_path = os.path.join(upload_dir, filename)

        if not os.path.exists(file_path):
            print(f"Erro: O arquivo '{filename}' não foi encontrado na pasta '{upload_dir}'.")
            return

        # O protocolo TFTP envia apenas o nome do arquivo para o servidor, não o caminho local
        request = b'\x00\x02' + filename.encode() + b'\x00octet\x00'
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        loop = asyncio.get_running_loop()

        print(f"Enviando '{filename}' de '{upload_dir}' para o servidor...")
        await loop.sock_sendto(sock, request, (self.host, self.port))

        # Espera o ACK inicial (bloco 0)
        try:
            data, addr = await asyncio.wait_for(loop.sock_recvfrom(sock, 512), timeout=5)
            packet = TFTPPacket.parse(data)

            if packet.get('opcode') == 4 and packet.get('block') == 0:
                with open(file_path, 'rb') as f:
                    block_num = 1
                    while True:
                        chunk = f.read(self.block_size)
                        data_pkt = TFTPPacket.data(block_num, chunk)
                        await loop.sock_sendto(sock, data_pkt, addr)

                        resp, _ = await loop.sock_recvfrom(sock, 512)
                        ack = TFTPPacket.parse(resp)
                        
                        if ack.get('opcode') == 4 and ack.get('block') == block_num:
                            block_num += 1
                            if len(chunk) < self.block_size:
                                print("Upload concluído com sucesso!")
                                break
            elif packet.get('opcode') == 5:
                print(f"Servidor recusou: {data[4:-1].decode()}")
        except asyncio.TimeoutError:
            print("Erro: O servidor não respondeu à solicitação de upload.")

async def main():
    parser = argparse.ArgumentParser(description="Cliente TFTP CLI")
    parser.add_argument("host", help="Endereço IP do servidor")
    parser.add_argument("action", choices=["get", "put"], help="Ação a realizar")
    parser.add_argument("filename", help="Nome do arquivo")
    parser.add_argument("--port", type=int, default=6969, help="Porta UDP")

    args = parser.parse_args()
    
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    if not os.path.exists("upload"):
        os.makedirs("upload")

    client = TFTPClient(args.host, args.port)
    if args.action == "get":
        await client.get(args.filename)
    else:
        await client.put(args.filename)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass