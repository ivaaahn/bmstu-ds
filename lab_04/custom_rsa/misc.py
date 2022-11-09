import math


def read_original(name: str, ext: str) -> bytes:
    with open(f"{name}.{ext}", "rb") as f:
        buffer = f.read()

    return buffer


def read_encrypted(name: str, ext: str) -> list[int]:
    with open(f"{name}.{ext}", "r") as f:
        buffer = f.read()

    return split_encrypted(buffer)


def read_encrypted2(name: str, ext: str) -> list[int]:
    with open(f"{name}.{ext}", "rb") as f:
        buffer = f.read()

    return split_encrypted2(buffer)


def split_encrypted2(data: bytes, delim: str = ",") -> list[int]:
    return list(map(lambda item: item.from_bytes, data.split(delim)))


def write_decrypted(name: str, ext: str, data: list[int] | bytes) -> None:
    with open(f"{name}_decrypted.{ext}", "wb") as f:
        f.write(bytes(data))


def write_encrypted(name: str, ext: str, data: list[int]) -> None:
    with open(f"{name}_encrypted.{ext}", "w") as f:
        f.write(join_encrypted(data))


def write_encrypted2(name: str, ext: str, data: list[int]) -> None:
    res = b""
    for item in data:
        bytes_required = max(1, math.ceil(item.bit_length() / 8))
        res += int.to_bytes(item, bytes_required, "big")

    with open(f"{name}_encrypted.{ext}", "wb") as f:
        f.write(res)


def join_encrypted(data: list[int], delim: str = ",") -> str:
    return delim.join(list(map(str, data)))


def split_encrypted(data: str, delim: str = ",") -> list[int]:
    return list(map(int, data.split(delim)))
