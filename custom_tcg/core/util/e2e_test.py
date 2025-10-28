"""Shared test helper utilities for E2E tests.

These helpers encapsulate common choice navigation patterns used by tests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_tcg.core.game import Game
    from custom_tcg.core.interface import IAction


def end_current_process(g: Game) -> list[IAction]:
    """Choose End Process for the current process and return next choices."""
    choices = g.context.choices
    end = next(c for c in choices if c.name == "End Process")
    return g.choose(end)


def choose_by_name_contains(g: Game, text: str) -> list[IAction]:
    """Choose the first action whose name contains the given text."""
    action = next(c for c in g.context.choices if text in c.name)
    return g.choose(action)


def choose_option_then_confirm(
    g: Game,
    option_name: str,
    *,
    max_steps: int,
) -> bool:
    """Find a specific Select option, choose it, then Confirm.

    Returns True if the option was chosen and confirmed; otherwise False after
    exhausting steps.
    """
    steps = 0
    while steps <= max_steps:
        option = next(
            (c for c in g.context.choices if c.name == option_name),
            None,
        )
        if option is not None:
            g.choose(option)
        confirm = next(
            (c for c in g.context.choices if c.name == "Confirm"),
            None,
        )
        if confirm is not None:
            g.choose(confirm)
            return True

        steps += 1

    return False


def choose_option_n_then_confirm(
    g: Game,
    option_name: str,
    count: int,
    *,
    max_steps: int,
) -> bool:
    """Choose `count` options by name then confirm (for accept_n > 1)."""
    chosen = 0
    steps = 0
    while steps <= max_steps:
        option = next(
            (c for c in g.context.choices if c.name == option_name),
            None,
        )
        if option is not None and chosen < count:
            g.choose(option)
            chosen += 1
        if chosen == count:
            confirm = next(
                (c for c in g.context.choices if c.name == "Confirm"),
                None,
            )
            if confirm is not None:
                g.choose(confirm)
                if chosen >= count:
                    return True

        steps += 1

    return False


def step_until_available(
    g: Game,
    end: str = "End Process",
    *,
    max_steps: int,
) -> None:
    """Step through choices until the specified choice is available."""
    initial_choices = [c.name for c in g.context.choices]
    end_initially_present = any(n == end for n in initial_choices)
    changed_observed = False

    steps = 0
    while True:
        names = [c.name for c in g.context.choices]
        if any(n == end for n in names):
            break

        cancel = next(
            (c for c in g.context.choices if c.name == "Cancel"),
            None,
        )
        if cancel is not None:
            g.choose(cancel)
        else:
            other = next(
                (c for c in g.context.choices if c.name != end),
                None,
            )
            if other is None:
                break
            g.choose(other)

        new_names = [c.name for c in g.context.choices]
        if new_names != names:
            changed_observed = True

        steps += 1
        assert steps <= max_steps, "Exceeded dynamic choice step safety limit"

    if not end_initially_present:
        assert changed_observed, "Expected choices to change at least once"


def play_card(g: Game, name: str) -> None:
    """Play a card by name from hand."""
    choose_by_name_contains(g, f"Play '{name}'")
    played = [c for c in g.context.player.played if c.name == name]
    assert played, f"Expected a {name} to be found in play"
