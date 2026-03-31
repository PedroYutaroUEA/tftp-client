import struct


class TFTPPacket:
    """
    TFTP Core Class
    """

    RRQ = 1
    WRQ = 2
    DATA = 3
    ACK = 4
    ERROR = 5

    @staticmethod
    def pack_rrq(filename: str, mode: str = "octet") -> bytes:
        return struct.pack(
            f"!H{len(filename)}sb{len(mode)}sb",
            TFTPPacket.RRQ,
            filename.encode(),
            0,
            mode.encode(),
            0,
        )

    @staticmethod
    def pack_wrq(filename: str, mode: str = "octet") -> bytes:
        return struct.pack(
            f"!H{len(filename)}sb{len(mode)}sb",
            TFTPPacket.WRQ,
            filename.encode(),
            0,
            mode.encode(),
            0,
        )

    @staticmethod
    def pack_ack(block_num: int) -> bytes:
        return struct.pack("!HH", TFTPPacket.ACK, block_num)

    @staticmethod
    def pack_data(block_num: int, data: bytes) -> bytes:
        header = struct.pack("!HH", TFTPPacket.DATA, block_num)
        return header + data

    @staticmethod
    def parse(data: bytes):
        opcode = struct.unpack("!H", data[:2])[0]
        return {"opcode": opcode, "raw": data}
