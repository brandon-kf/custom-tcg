"""Utility functions."""

from __future__ import annotations

from secrets import randbelow


def list_randomize(ordered: list) -> list:
    """Randomize the order of items in a list."""
    output: list = []
    sort_indexes: list[tuple[int, int]] = [
        (i, randbelow(exclusive_upper_bound=101)) for i in range(len(ordered))
    ]
    sort_indexes = sorted(sort_indexes, key=lambda x: x[1])
    for src_index, _ in sort_indexes:
        output.append(ordered[src_index])
    return output
