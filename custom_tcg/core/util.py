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


def to_dict(obj: object) -> dict:
    """Serialize complex objects into nested json dictionaries."""
    result: dict | list | str | int | float | bool | None = to_dict_recurse(
        obj=obj,
    )
    if isinstance(result, dict):
        return result
    msg = "Object could not be converted to a dictionary."
    raise TypeError(msg)


def to_dict_recurse(
    obj: object,
) -> dict | list | str | int | float | bool | None:
    """Serialize complex objects into nested json dictionaries."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {key: to_dict_recurse(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_dict_recurse(item) for item in obj]
    if hasattr(obj, "__dict__"):
        return to_dict_recurse(obj.__dict__)
    return str(obj)
