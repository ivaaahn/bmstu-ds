import functools
import heapq
import json
from collections import Counter
from pprint import pprint
from typing import Optional

import click


@functools.total_ordering
class Node:
    def __init__(
        self,
        key: int | None,
        value: int,
        left: Optional["Node"] = None,
        right: Optional["Node"] = None,
    ) -> None:
        self.key = key
        self.value = value
        self.right = right
        self.left = left

    @property
    def is_leaf(self) -> bool:
        return self.key is not None

    def __lt__(self, other: "Node") -> bool:
        return self.value < other.value

    def __str__(self) -> str:
        return f"({self.key}, {self.value})"

    def display(self):
        lines, *_ = self._display_aux()
        for line in lines:
            print(line)

    def _display_aux(self):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        # No child.
        if self.right is None and self.left is None:
            line = "%s" % self.key
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            s = "%s" % self.key
            u = len(s)
            first_line = (x + 1) * " " + (n - x - 1) * "_" + s
            second_line = x * " " + "/" + (n - x - 1 + u) * " "
            shifted_lines = [line + u * " " for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            s = "%s" % self.key
            u = len(s)
            first_line = s + x * "_" + (n - x) * " "
            second_line = (u + x) * " " + "\\" + (n - x - 1) * " "
            shifted_lines = [u * " " + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        s = "%s" % self.key
        u = len(s)
        first_line = (x + 1) * " " + (n - x - 1) * "_" + s + y * "_" + (m - y) * " "
        second_line = (
            x * " " + "/" + (n - x - 1 + u + y) * " " + "\\" + (m - y - 1) * " "
        )
        if p < q:
            left += [n * " "] * (q - p)
        elif q < p:
            right += [m * " "] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * " " + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2


def print_tree(node, level=0):
    if node != None:
        print_tree(node.left, level + 1)
        print(" " * 4 * level + "/")
        print(" " * 4 * level + "--> " + str(node.value))
        print(" " * 4 * level + "\\")
        print_tree(node.right, level + 1)


def create_tree(freq: dict[int | str, int]) -> Node:
    nodes = [Node(int(k), v) for k, v in freq.items()]
    heapq.heapify(nodes)

    while len(nodes) > 1:
        right = heapq.heappop(nodes)
        left = heapq.heappop(nodes)

        heapq.heappush(nodes, Node(None, right.value + left.value, left, right))

    return nodes[0]


def calculate_freq(text: bytes) -> dict[int, int]:
    return dict(Counter(text))


def node_to_code(node: Node, prefix: str = "", cnt=0) -> dict[int, str]:
    codes: dict[int, str] = {}

    if not (node.left or node.right or prefix):
        return {node.key: "1"}

    if node.is_leaf:
        return {node.key: prefix}

    codes.update(node_to_code(node.left, prefix + "0", cnt + 1))
    codes.update(node_to_code(node.right, prefix + "1", cnt + 1))

    return codes


def compress_data(text: bytes, codes: dict[int, str]) -> bytes:
    bits = "".join((codes[letter] for letter in text))

    res: list[int] = []
    byte, counter = 0, 7
    for bit in bits:
        byte = byte << 1 | int(bit)
        counter -= 1

        if counter < 0:
            res.append(byte)
            byte, counter = 0, 7

    remainder = (6 - counter) % 8

    if remainder != 7:
        res.append(byte)

    res.append(remainder)

    return bytes(res)


def decompress_data(compressed: bytes, root: Node) -> bytes:
    decompressed: list[int] = []
    curr_node = root

    for idx in range(len(compressed) - 1):
        byte = compressed[idx]

        bit_pos_start = 7 if idx != (len(compressed) - 2) else compressed[-1]
        for bit_cnt in range(bit_pos_start, -1, -1):
            bit = byte >> bit_cnt & 1

            # if one symbol
            if root.is_leaf:
                decompressed.append(curr_node.key)
                continue

            if bit == 0:
                curr_node = curr_node.left
            elif bit == 1:
                curr_node = curr_node.right

            if curr_node.is_leaf:
                decompressed.append(curr_node.key)
                curr_node = root

    return bytes(decompressed)


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "--compress",
    is_flag=True,
    show_default=True,
    default=False,
    help="Compress data.",
)
@click.option(
    "--decompress",
    is_flag=True,
    show_default=True,
    default=False,
    help="Decompress data.",
)
def run(filename: str, compress: bool = False, decompress: bool = False):
    if compress == decompress:
        click.secho("\nBad params", fg="red", bold=True)
        return

    with open(filename, "rb") as f:
        data = f.read()
        click.secho(len(data), fg="yellow", bold=True)

    if not data:
        click.secho("\nBad params", fg="red", bold=True)
        return

    name, ext = filename.split(".")
    if compress:
        freq = calculate_freq(data)
        root_node = create_tree(freq)
        codes = node_to_code(root_node)

        print("=================================")
        for key, value in sorted(list(freq.items()), key=lambda x: x[1]):
            print(f"{key} --- {value} ({codes[key]})")
        print("=================================")

        compressed = compress_data(data, codes)
        freq_bytes = json.dumps(freq).encode()
        freq_len = len(freq_bytes)
        res = freq_len.to_bytes(2, "big") + freq_bytes + compressed
        with open(f"{name}_compressed.{ext}", "wb") as f:
            f.write(res)
            click.secho(len(res), fg="yellow", bold=True)
            click.secho(len(compressed), fg="yellow", bold=True)

        click.secho("\nCompressed", fg="green", bold=True)

    if decompress:
        freq_len = int.from_bytes(data[:2], "big")
        freq, compressed = (
            json.loads(data[2 : 2 + freq_len]),
            data[2 + freq_len :],
        )
        root_node = create_tree(freq)
        decompressed = decompress_data(compressed, root_node)

        with open(f"{name}_decompressed.{ext}", "wb") as f:
            f.write(decompressed)
            click.secho(len(data), fg="yellow", bold=True)

        click.secho("\nDecompressed", fg="green", bold=True)


if __name__ == "__main__":
    run()
