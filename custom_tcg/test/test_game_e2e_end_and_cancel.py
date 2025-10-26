"""End-to-end test for three full game turns using the Game API.

Only randomness is mocked to keep turn order and deck order deterministic.
The test drives Game.setup/start/choose and validates process rotation and
player turn order over three full turns (Play then Rest for a player).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from custom_tcg import game as game_mod
from custom_tcg.common.being.aimless_wanderer import AimlessWanderer
from custom_tcg.common.being.that_pebble_girl import ThatPebbleGirl
from custom_tcg.core import util as util_mod
from custom_tcg.core.anon import Deck, Player
from custom_tcg.core.process.lets_play import LetsPlay
from custom_tcg.core.process.lets_rest import LetsRest
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

    # Manually create two players and their starting decks
    p1 = Player(
        session_object_id="p1",
        name="Person 1",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )

    p1_deck = Deck(
        name="Deck 1",
        player=p1,
        starting=[
            LetsPlay.create(player=p1),
            LetsRest.create(player=p1),
            AimlessWanderer.create(player=p1),
        ],
        main=[
            AimlessWanderer.create(player=p1),
        ],
    )
    p1.decks.append(p1_deck)
    p1.select_deck(deck=p1_deck)

    p2 = Player(
        session_object_id="p2",
        name="Person 2",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )

    p2_deck = Deck(
        name="Deck 2",
        player=p2,
        starting=[
            LetsPlay.create(player=p2),
            LetsRest.create(player=p2),
            ThatPebbleGirl.create(player=p2),
        ],
        main=[
            ThatPebbleGirl.create(player=p2),
        ],
    )
    p2.decks.append(p2_deck)
    p2.select_deck(deck=p2_deck)

    g = Game(players=[p1, p2])
    g.setup()
    return g


def _end_current_process(g: Game) -> list[IAction]:
    """Choose End Process for the current process and return next choices."""
    choices = g.context.choices
    end = next(c for c in choices if c.name == "End Process")
    return g.choose(end)


def _choose_by_name_contains(g: Game, text: str) -> list[IAction]:
    """Choose the first action whose name contains the given text."""
    action = next(c for c in g.context.choices if text in c.name)
    return g.choose(action)


def _step_until_end_available(g: Game, *, max_steps: int) -> None:
    """Advance through dynamic choices until End Process is available again.

    Prefer selecting Cancel when available. Asserts that choice lists change
    at least once if End Process wasn't initially present.
    """
    initial_choices = [c.name for c in g.context.choices]
    end_initially_present = any(n == "End Process" for n in initial_choices)
    changed_observed = False

    steps = 0
    while True:
        names = [c.name for c in g.context.choices]
        if any(n == "End Process" for n in names):
            break

        # Prefer a cancel if available to move selectors along.
        cancel = next(
            (c for c in g.context.choices if c.name == "Cancel"),
            None,
        )
        if cancel is not None:
            g.choose(cancel)
        else:
            other = next(
                (c for c in g.context.choices if c.name != "End Process"),
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

        # Execute specific non-End actions during Play
        if g.context.player.name == "Person 1":
            # Activate Aimless Wanderer (was auto-played during start)
            _choose_by_name_contains(
                g,
                "Activate from card 'Aimless Wanderer'",
            )
            _step_until_end_available(g, max_steps=20)
        else:
            # Activate That Pebble Girl (was auto-played during start)
            _choose_by_name_contains(
                g,
                "Activate from card 'That Pebble Girl'",
            )
            _step_until_end_available(g, max_steps=20)

        # End Let's Play for current player
        choices = _end_current_process(g)
        assert choices, "Expected choices after ending Play process"

        # No additional Rest choices are expected; proceed to end Rest

        # End Let's Rest for current player
        choices = _end_current_process(g)
        assert choices, "Expected choices after ending Rest process"

    # With deterministic randomness, the order should be p1 -> p2 -> p1
    assert observed_turn_players[0] == "Person 1"
    assert observed_turn_players[1] == "Person 2"
    assert observed_turn_players[2] == "Person 1"
