import functools
import heapq
from collections import Counter
from pprint import pprint
from typing import Optional


@functools.total_ordering
class Node:
    def __init__(
        self,
        key: int,
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
        return self.key != b""

    def __lt__(self, other: "Node") -> bool:
        return self.value < other.value

    def __str__(self) -> str:
        return f"({self.key}, {self.value})"


def create_tree(freq: dict[int, int]) -> Node:
    nodes = [Node(k, v) for k, v in freq.items()]
    heapq.heapify(nodes)

    while len(nodes) > 1:
        right = heapq.heappop(nodes)
        left = heapq.heappop(nodes)

        heapq.heappush(nodes, Node(b"", right.value + left.value, left, right))

    return nodes[0]


def calculate_freq(text: bytes) -> dict[int, int]:
    return dict(Counter(text))


def node_to_code(node: Node, prefix: str = "") -> dict[int, str]:
    codes: dict[int, str] = {}

    try:
        if node.is_leaf:
            return {node.key: prefix}
    except:
        print(1)

    codes.update(node_to_code(node.left, prefix + "0"))
    codes.update(node_to_code(node.right, prefix + "1"))

    return codes


def compress(text: bytes, codes: dict[int, str]) -> str:
    compressed = ""
    for letter in text:
        compressed += codes[letter]

    return compressed


def decompress(compressed: str, root: Node) -> list[int]:
    decompressed: list[int] = []
    curr_node = root

    idx = 0
    while idx < len(compressed):
        if compressed[idx] == "0":
            curr_node = curr_node.left
        else:
            curr_node = curr_node.right

        if curr_node.is_leaf:
            decompressed.append(curr_node.key)
            curr_node = root

        idx += 1

    return decompressed


def run():
    with open("img.png", "rb") as f:
        text = f.read()

    freq = calculate_freq(text)
    root_node = create_tree(freq)
    codes = node_to_code(root_node)
    compressed = compress(text, codes)
    decompressed = decompress(compressed, root_node)
    with open("img_2.png", "wb") as f:
        f.write(bytes(decompressed))


if __name__ == "__main__":
    run()
