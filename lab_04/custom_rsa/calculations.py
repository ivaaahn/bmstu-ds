import hashlib
import itertools
from collections.abc import Callable, Iterable, Sequence
from multiprocessing import Pool

NUM_THREADS = 10


def power_log_n(x: int, y: int, p: int) -> int:
    res = 1  # Initialize result

    # Update x if it is more
    # than or equal to p
    x = x % p

    if x == 0:
        return 0

    while y > 0:

        # If y is odd, multiply
        # x with result
        if (y & 1) == 1:
            res = (res * x) % p

        # y must be even now
        y = y >> 1  # y = y/2
        x = (x * x) % p

    return res


def split_to_parallel(data: Sequence, num: int = NUM_THREADS) -> Iterable:
    for i in range(0, len(data), num):
        yield data[i : i + num]


def pow_list(
    data: list[int], b: int, c: int, pow_func: Callable[[int, int, int], int]
) -> list[int]:
    return [pow_func(x, b, c) for x in data]


def pow_in_executor(
    data: list[int] | bytes,
    b: int,
    c: int,
    *,
    num: int = NUM_THREADS,
    pow_func: Callable[[int, int, int], int] = pow
) -> list[int]:
    with Pool(processes=num) as pool:
        results = pool.starmap(
            pow_list,
            [
                (chunk, b, c, pow_func)
                for chunk in split_to_parallel(data, len(data) // num + 1)
            ],
        )
    return list(itertools.chain.from_iterable(results))


def hasher(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()
