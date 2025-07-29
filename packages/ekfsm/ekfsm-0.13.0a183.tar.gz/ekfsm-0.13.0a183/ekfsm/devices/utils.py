from crcmod.predefined import Crc
from typing import Sequence


def compute_int_from_bytes(data: Sequence[int]) -> int:
    # Combine the bytes into a single integer
    result = 0
    for num in data:
        result = (result << 8) | num
    return result


def get_crc16_xmodem(data: bytes) -> int:
    crc16_xmodem = Crc("xmodem")
    crc16_xmodem.update(data)
    return crc16_xmodem.crcValue
