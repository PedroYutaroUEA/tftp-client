import struct
from src.core.infra import TFTPPacket


class TFTPEngine:
    """Implementação manual do protocolo TFTP (Core). Usando Injeção de Conexão."""

    def __init__(self, connection, block_size=512):
        self.conn = connection
        self.block_size = block_size

    async def list_remote_files(self, path):
        """Envia requisição de listagem e retorna string com nomes dos arquivos"""
        self.conn.open()
        pkt = TFTPPacket.pack_list_request(path)
        await self.conn.send(pkt)

        content = b""
        expected_block = 1

        try:
            while True:
                # Esperamos um pacote DATA ou ERROR
                data, addr = await self.conn.receive(self.block_size + 4)
                res = TFTPPacket.parse(data)

                if res["opcode"] == TFTPPacket.DATA:
                    block_num = struct.unpack("!H", data[2:4])[0]
                    if block_num == expected_block:
                        content += data[4:]
                        # Envia ACK para o servidor saber que recebemos a parte da lista
                        ack = TFTPPacket.pack_ack(block_num)
                        await self.conn.send(ack, addr)
                        expected_block += 1

                        if len(data[4:]) < self.block_size:
                            break
                elif res["opcode"] == TFTPPacket.ERROR:
                    raise Exception(f"Servidor recusou listagem: {data[4:-1].decode()}")
            return content.decode("utf-8")
        except Exception as e:
            raise Exception(f"Erro na listagem remota: {e}")

    async def read_file(self, filename, write_callback):
        """Lógica RRQ"""
        self.conn.open()
        pkt = TFTPPacket.pack_rrq(filename)
        await self.conn.send(pkt)

        expected_block = 1
        while True:
            data, addr = await self.conn.receive(self.block_size + 4)
            res = TFTPPacket.parse(data)

            if res["opcode"] == TFTPPacket.DATA:
                block_num = struct.unpack("!H", data[2:4])[0]
                if block_num == expected_block:
                    payload = data[4:]
                    write_callback(payload)
                    # Envia ACK
                    ack = TFTPPacket.pack_ack(block_num)
                    await self.conn.send(ack, addr)
                    print(f"  [ACK] Bloco {block_num} recebido ({len(payload)} bytes)")
                    expected_block += 1

                    if len(payload) < self.block_size:
                        break
            elif res["opcode"] == TFTPPacket.ERROR:
                raise Exception(f"Erro do Servidor: {data[4:-1].decode()}")

    async def write_file(self, filename, read_callback):
        """Lógica WRQ"""
        self.conn.open()
        pkt = TFTPPacket.pack_wrq(filename)
        await self.conn.send(pkt)

        # Espera ACK 0
        resp, addr = await self.conn.receive()

        block_num = 1
        while True:
            chunk = read_callback(self.block_size)
            if not chunk and block_num > 1:
                break  # Fim do arquivo

            data_pkt = TFTPPacket.pack_data(block_num, chunk)
            await self.conn.send(data_pkt, addr)

            # Espera ACK
            resp, _ = await self.conn.receive()
            print(f"  [SENT] Bloco {block_num} enviado.")

            block_num += 1
            if len(chunk) < self.block_size:
                break
