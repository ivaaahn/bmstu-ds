import math
from multiprocessing import Pool
from typing import List

from custom_rsa.calculations import split_to_parallel

ENCRYPTED_POSTFIX = "encrypted"
SIGNED_POSTFIX = "signed"
DECRYPTED_POSTFIX = "decrypted"


def read_original(name: str, ext: str) -> bytes:
    with open(f"{name}.{ext}", "rb") as f:
        buffer = f.read()

    return buffer


def read_encrypted(
    name: str, ext: str, size: int, postfix: str = ENCRYPTED_POSTFIX
) -> list[int]:
    with open(f"{name}_{postfix}.{ext}", "rb") as f:
        buffer = f.read()

    return split_encrypted(buffer, size)


def split_encrypted(data: bytes, size: int) -> list[int]:
    res: list[int] = []
    for i in range(0, len(data), size):
        byte = data[i : i + size]
        res.append(int.from_bytes(byte, "big"))

    return res


def write_decrypted(
    name: str,
    ext: str,
    data: list[int] | bytes,
    postfix: str = DECRYPTED_POSTFIX,
) -> None:
    with open(f"{name}_{postfix}.{ext}", "wb") as f:
        f.write(bytes(data))


def converter_to_bytes(x, num_bytes):
    res = b""
    for item in x:
        res += int.to_bytes(item, num_bytes, "big")
    return res


def write_encrypted(
    name: str,
    ext: str,
    data: list[int],
    num_bytes: int,
    postfix: str = ENCRYPTED_POSTFIX,
) -> None:
    data_len = len(data)
    processes = max(1, min(10, data_len))
    with Pool(processes=processes) as pool:
        results = pool.starmap(
            converter_to_bytes,
            [
                (chunk, num_bytes)
                for chunk in split_to_parallel(data, data_len // processes)
            ],
        )

    res = b"".join(results)

    with open(f"{name}_{postfix}.{ext}", "wb") as f:
        f.write(res)


def write_signed(name: str, ext: str, data: list[int], num_bytes: int) -> None:
    return write_encrypted(name, ext, data, num_bytes, postfix=SIGNED_POSTFIX)


def read_signed(name: str, ext: str, size: int) -> list[int]:
    return read_encrypted(name, ext, size, postfix=SIGNED_POSTFIX)
