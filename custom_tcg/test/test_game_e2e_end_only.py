"""End-to-end test for three full game turns using the Game API.

Only randomness is mocked to keep turn order and deck order deterministic.
The test drives Game.setup/start/choose and validates process rotation and
player turn order over three full turns (Play then Rest for a player).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from custom_tcg import game as game_mod
from custom_tcg.common.player import p1, p2
from custom_tcg.core import util as util_mod
from custom_tcg.game import Game

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction


@pytest.fixture
def game(monkeypatch: pytest.MonkeyPatch) -> Game:
    """Create a deterministic game instance for testing turns."""

    def identity_randomize(*, ordered: list) -> list:  # match signature
        return list(ordered)

    monkeypatch.setattr(util_mod, "list_randomize", identity_randomize)

    # Ensure first player selection is deterministic (p1 goes first)
    def fake_randbelow(*, exclusive_upper_bound: int) -> int:  # noqa: ARG001
        return 0

    monkeypatch.setattr(game_mod, "randbelow", fake_randbelow)
    monkeypatch.setattr(util_mod, "randbelow", fake_randbelow)

    g = Game(players=[p1(), p2()])
    g.setup()
    return g


def _end_current_process(g: Game) -> list[IAction]:
    """Choose End Process for the current process and return next choices."""
    choices = g.context.choices
    end = next(c for c in choices if c.name == "End Process")
    return g.choose(end)


def test_three_full_turns_via_game_api(game: Game) -> None:
    """Drive three full turns: Play->Rest per turn, rotating players.

    Asserts:
    - First player is p1 after deterministic setup.
    - Each turn ends after ending Play then Rest for that player.
    - Player order cycles p1 -> p2 -> p1 over three turns.
    """
    g = game

    # Start the game: this queues and activates the first process
    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    observed_turn_players: list[str] = []
    TURN_COUNT = 3  # noqa: N806 - test-local constant

    for _ in range(TURN_COUNT):
        # Record current player at the start of their Play process
        observed_turn_players.append(g.context.player.name)

        # End Let's Play for current player
        choices = _end_current_process(g)
        assert choices, "Expected choices after ending Play process"

        # End Let's Rest for current player
        choices = _end_current_process(g)
        assert choices, "Expected choices after ending Rest process"

    # With deterministic randomness, the order should be p1 -> p2 -> p1
    assert observed_turn_players[0] == "Person 1"
    assert observed_turn_players[1] == "Person 2"
    assert observed_turn_players[2] == "Person 1"
