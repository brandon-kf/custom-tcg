"""Extended e2e with explicit Discover Trail and Deliver flows (4 turns).

Based on `test_game_e2e_complex1.py`, this runs four full turns and adds:
- Aimless Wanderer: Discover a 'Trail' (discard a held 'Stick').
- That Pebble Girl: Deliver a held 'Pebble' to another being (Peasant).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from custom_tcg import game as game_mod
from custom_tcg.common.being.aimless_wanderer import AimlessWanderer
from custom_tcg.common.being.peasant import Peasant
from custom_tcg.common.being.that_pebble_girl import ThatPebbleGirl
from custom_tcg.common.effect.held import Held
from custom_tcg.common.item.pebble import Pebble
from custom_tcg.common.item.stick import Stick
from custom_tcg.common.item.trail import Trail
from custom_tcg.core import util as util_mod
from custom_tcg.core.anon import Deck, Player
from custom_tcg.core.process.lets_play import LetsPlay
from custom_tcg.core.process.lets_rest import LetsRest
from custom_tcg.game import Game

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction


@pytest.fixture
def game(monkeypatch: pytest.MonkeyPatch) -> Game:
    """Create a deterministic game instance for testing four full turns."""

    def identity_randomize(*, ordered: list) -> list:
        return list(ordered)

    monkeypatch.setattr(util_mod, "list_randomize", identity_randomize)

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
            Peasant.create(player=p2),  # Receiver for Deliver
        ],
        main=[
            ThatPebbleGirl.create(player=p2),
            Peasant.create(player=p2),
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

    Prefer selecting Cancel when available. Asserts choices change at least
    once if End Process wasn't initially present.
    """
    initial_choices = [c.name for c in g.context.choices]
    end_initially_present = any(n == "End Process" for n in initial_choices)
    changed_observed = False

    steps = 0
    while True:
        names = [c.name for c in g.context.choices]
        if any(n == "End Process" for n in names):
            break

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


def _choose_option_then_confirm(
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
                return False
            g.choose(other)

        steps += 1

    return False


def _aw_create_stick(g: Game) -> None:
    """Aimless Wanderer creates and holds a Stick (explicit choices)."""
    _choose_by_name_contains(
        g,
        "Activate from card 'Aimless Wanderer'",
    )
    assert _choose_option_then_confirm(
        g,
        "Select 'Stick'",
        max_steps=40,
    ), "Expected to select 'Stick' and confirm"
    assert _choose_option_then_confirm(
        g,
        "Select 'Pile of Wood'",
        max_steps=40,
    ), "Expected to select 'Pile of Wood' and confirm"
    _step_until_end_available(g, max_steps=40)

    sticks = [c for c in g.context.player.played if isinstance(c, Stick)]
    assert sticks, "Expected a Stick to be created"
    held = next((e for e in sticks[0].effects if isinstance(e, Held)), None)
    assert held is not None
    assert held.card_held_by.name == "Aimless Wanderer"


def _aw_discover_trail(g: Game) -> None:
    """Aimless Wanderer discovers a Trail by discarding a Stick."""
    _choose_by_name_contains(
        g,
        "Activate from card 'Aimless Wanderer'",
    )
    assert _choose_option_then_confirm(
        g,
        "Select 'Trail'",
        max_steps=60,
    ), "Expected to select 'Trail' and confirm"
    assert _choose_option_then_confirm(
        g,
        "Select 'Stick'",
        max_steps=60,
    ), "Expected to select 'Stick' (for discard) and confirm"
    _step_until_end_available(g, max_steps=60)

    trails = [c for c in g.context.player.played if isinstance(c, Trail)]
    assert trails, "Expected a Trail to be created"
    # Trail is extremely heavy; Aimless Wanderer cannot hold it (by design).
    held = next((e for e in trails[0].effects if isinstance(e, Held)), None)
    assert held is None


def _tpg_create_pebble(g: Game) -> None:
    """Create and hold a Pebble with That Pebble Girl (explicit choices)."""
    _choose_by_name_contains(
        g,
        "Activate from card 'That Pebble Girl'",
    )
    assert _choose_option_then_confirm(
        g,
        "Select 'Pebble'",
        max_steps=40,
    ), "Expected to select 'Pebble' and confirm"
    assert _choose_option_then_confirm(
        g,
        "Select 'Pile of Rocks'",
        max_steps=40,
    ), "Expected to select 'Pile of Rocks' and confirm"
    _step_until_end_available(g, max_steps=40)

    pebbles = [c for c in g.context.player.played if isinstance(c, Pebble)]
    assert pebbles, "Expected a Pebble to be created"
    held = next((e for e in pebbles[0].effects if isinstance(e, Held)), None)
    assert held is not None
    assert held.card_held_by.name == "That Pebble Girl"


def _tpg_deliver_pebble_to_peasant(g: Game) -> None:
    """Deliver a held Pebble from That Pebble Girl to the Peasant."""
    _choose_by_name_contains(
        g,
        "Activate from card 'That Pebble Girl'",
    )
    assert _choose_option_then_confirm(
        g,
        "Select 'Peasant'",
        max_steps=60,
    ), "Expected to select 'Peasant' as receiver and confirm"
    assert _choose_option_then_confirm(
        g,
        "Select 'Pebble'",
        max_steps=60,
    ), "Expected to select 'Pebble' to deliver and confirm"
    _step_until_end_available(g, max_steps=60)

    pebbles = [c for c in g.context.player.played if isinstance(c, Pebble)]
    assert pebbles, "Expected a Pebble to be present"
    held = next((e for e in pebbles[0].effects if isinstance(e, Held)), None)
    assert held is not None
    assert held.card_held_by.name == "Peasant"


def test_four_turns_with_selects_discover_trail_and_deliver(
    game: Game,
) -> None:
    """Run four turns with explicit select/confirm, discover, and deliver.

    - Turn 1 (P1/AW): Create and hold a Stick.
    - Turn 2 (P2/TPG): Create and hold a Pebble.
    - Turn 3 (P1/AW): Discover a Trail by discarding the Stick.
    - Turn 4 (P2/TPG): Deliver the Pebble to the Peasant.
    """
    g = game

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    observed_turn_players: list[str] = []
    turn_count = 4

    for turn_index in range(turn_count):
        observed_turn_players.append(g.context.player.name)

        if g.context.player.name == "Person 1":
            if turn_index == 0:
                _aw_create_stick(g)
            else:
                _aw_discover_trail(g)

        elif turn_index == 1:
            _tpg_create_pebble(g)
        else:
            _tpg_deliver_pebble_to_peasant(g)

        # End Let's Play for current player
        choices = _end_current_process(g)
        assert choices, "Expected choices after ending Play process"

        # End Let's Rest for current player
        choices = _end_current_process(g)
        assert choices, "Expected choices after ending Rest process"

    assert observed_turn_players == [
        "Person 1",
        "Person 2",
        "Person 1",
        "Person 2",
    ]
