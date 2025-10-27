"""E2E: Desperate Shepherd finds/shears, Seamstress crafts cord and cloth.

This scenario demonstrates a multi-turn flow:
- Desperate Shepherd: search for a Sheep (force success deterministically).
- Desperate Shepherd: shear the Sheep to create a Bundle of Wool.
- Desperate Shepherd: separate a Ball of Wool and deliver it to Seamstress.
- Seamstress: wind fibers into Cord (discard the Ball of Wool).
- Repeat delivery to produce a second Cord.
- Seamstress: weave cords into Cloth (discard 2 Cords).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from custom_tcg import game as game_mod
from custom_tcg.common.being import desperate_shepherd as ds_mod
from custom_tcg.common.being.desperate_shepherd import DesperateShepherd
from custom_tcg.common.being.peasant import Peasant
from custom_tcg.common.being.seamstress import Seamstress
from custom_tcg.common.being.sheep import Sheep
from custom_tcg.common.effect.held import Held
from custom_tcg.common.item.bundle_of_wool import BundleOfWool
from custom_tcg.common.item.cloth import Cloth
from custom_tcg.common.item.cord import Cord
from custom_tcg.core import util as util_mod
from custom_tcg.core.anon import Deck, Player
from custom_tcg.core.process.lets_play import LetsPlay
from custom_tcg.core.process.lets_rest import LetsRest
from custom_tcg.game import Game

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction


@pytest.fixture
def game(monkeypatch: pytest.MonkeyPatch) -> Game:
    """Create a deterministic game instance for Shepherd/Seamstress flow."""

    def identity_randomize(*, ordered: list) -> list:
        return list(ordered)

    monkeypatch.setattr(util_mod, "list_randomize", identity_randomize)

    def fake_randbelow(*, exclusive_upper_bound: int) -> int:  # noqa: ARG001
        return 0

    # Keep turn order stable
    monkeypatch.setattr(game_mod, "randbelow", fake_randbelow)
    monkeypatch.setattr(util_mod, "randbelow", fake_randbelow)

    # Force Shepherd's search success: needs randbelow(6)+1 == 6

    def shepherd_randbelow(*, exclusive_upper_bound: int) -> int:  # noqa: ARG001
        return 5  # 5 + 1 == 6

    monkeypatch.setattr(ds_mod, "randbelow", shepherd_randbelow)

    # Players and starting decks
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
            Peasant.create(player=p1),
        ],
        main=[
            Seamstress.create(player=p1),
            DesperateShepherd.create(player=p1),
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
        ],
        main=[
            # Provide a benign main card to satisfy init; p2 will no-op.
            Peasant.create(player=p2),
        ],
    )
    p2.decks.append(p2_deck)
    p2.select_deck(deck=p2_deck)

    g = Game(players=[p1, p2])
    g.setup()
    return g


def _end_current_process(g: Game) -> list[IAction]:
    choices = g.context.choices
    end = next(c for c in choices if c.name == "End Process")
    return g.choose(end)


def _choose_by_name_contains(g: Game, text: str) -> list[IAction]:
    action = next(c for c in g.context.choices if text in c.name)
    return g.choose(action)


def _step_until_available(
    g: Game,
    end: str = "End Process",
    *,
    max_steps: int,
) -> None:
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


def _choose_option_then_confirm(
    g: Game,
    option_name: str,
    *,
    max_steps: int,
) -> bool:
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


def _choose_option_n_then_confirm(
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
        # select until we reach the desired count
        option = next(
            (c for c in g.context.choices if c.name == option_name),
            None,
        )
        if option is not None and chosen < count:
            g.choose(option)
            chosen += 1
            # loop to select again before confirming
        else:
            confirm = next(
                (c for c in g.context.choices if c.name == "Confirm"),
                None,
            )
            if confirm is not None:
                g.choose(confirm)
                # If not enough selected, confirm will be rejected and
                # choices restored
                if chosen >= count:
                    return True

        cancel = next(
            (c for c in g.context.choices if c.name == "Cancel"),
            None,
        )
        if cancel is not None and chosen < count:
            # continue exploring; typically we won't need cancel here
            g.choose(cancel)
        else:
            other = next(
                (c for c in g.context.choices if c.name != "End Process"),
                None,
            )
            if other is None:
                return chosen >= count
            g.choose(other)

        steps += 1

    return False


def _play_card(g: Game, name: str) -> None:
    _choose_by_name_contains(g, f"Play '{name}'")
    # Search auto-resolves; step until the process offers end.

    played = [c for c in g.context.player.played if c.name == name]
    assert played, f"Expected a {name} to be found in play"


def _activate_desperate_shepherd(
    g: Game,
    separate: bool = False,  # noqa: FBT001, FBT002
    deliver: tuple[str, str] | None = None,
) -> None:
    _choose_by_name_contains(g, "Activate from card 'Desperate Shepherd'")

    # Search for sheep auto-resolves; no explicit choices.
    sheep = [c for c in g.context.player.played if isinstance(c, Sheep)]
    assert sheep, "Expected a Sheep to be found"

    # Shearing auto-executes via Tap (Select) + Find; no explicit choices.
    bundles = [
        c for c in g.context.player.played if isinstance(c, BundleOfWool)
    ]
    assert bundles, "Expected a Bundle of Wool to be created"
    held = next((e for e in bundles[0].effects if isinstance(e, Held)), None)
    assert held is not None
    assert held.card_held_by.name == "Desperate Shepherd"

    # If desired, Separate Ball of Wool (selector then cost), both via choices
    if separate:
        assert _choose_option_then_confirm(
            g,
            "Select 'Ball of Wool'",
            max_steps=40,
        ), "Expected to select 'Ball of Wool' and confirm"
        # Then, verify a held Bundle of Wool (cost)
        assert _choose_option_then_confirm(
            g,
            "Select 'Bundle of Wool'",
            max_steps=40,
        ), "Expected to select 'Bundle of Wool' and confirm"
    else:
        _step_until_available(g, "Select 'Peasant'", max_steps=60)

    # If desired, Deliver Ball of Wool  (deliver action auto-prompts)
    if deliver is not None:
        receiver_name, item_name = deliver
        assert _choose_option_then_confirm(
            g,
            f"Select '{receiver_name}'",
            max_steps=60,
        ), f"Expected to select '{receiver_name}' as receiver and confirm"
        assert _choose_option_then_confirm(
            g,
            f"Select '{item_name}'",
            max_steps=60,
        ), f"Expected to select '{item_name}' to deliver and confirm"

    _step_until_available(g, max_steps=60)


def _activate_seamstress(
    g: Game,
    find_cord: bool = False,  # noqa: FBT001, FBT002
    find_cloth: bool = False,  # noqa: FBT001, FBT002
) -> None:
    _choose_by_name_contains(g, "Activate from card 'Seamstress'")

    if find_cord:
        # Discard Ball of Wool (cost)
        assert _choose_option_then_confirm(
            g,
            "Select 'Ball of Wool'",
            max_steps=60,
        ), "Expected to select Ball of Wool to discard"
        # Choose to create Cord
        assert _choose_option_then_confirm(
            g,
            "Select 'Cord'",
            max_steps=60,
        ), "Expected to select 'Cord' and confirm"

        cords = [c for c in g.context.player.played if isinstance(c, Cord)]
        assert cords, "Expected a Cord to be created"
        held = next((e for e in cords[0].effects if isinstance(e, Held)), None)
        assert held is not None
        assert held.card_held_by.name == "Seamstress"
    else:
        _step_until_available(g, "Select 'Cord'", max_steps=60)

    if find_cloth:
        # Discard 2 Cords (cost requires accept_n=2)
        assert _choose_option_n_then_confirm(
            g,
            "Select 'Cord'",
            2,
            max_steps=80,
        ), "Expected to select two 'Cord' cards and confirm"
        # Choose to create Cloth
        assert _choose_option_then_confirm(
            g,
            "Select 'Cloth'",
            max_steps=60,
        ), "Expected to select 'Cloth' and confirm"

        cloths = [c for c in g.context.player.played if isinstance(c, Cloth)]
        assert cloths, "Expected a Cloth to be created"
        held = next((e for e in cloths[0].effects if isinstance(e, Held)), None)
        assert held is not None
        assert held.card_held_by.name == "Seamstress"

    _step_until_available(g, max_steps=60)


def test_shepherd_to_seamstress_crafting(game: Game) -> None:
    """End-to-end: Shepherd creates wool, Seamstress crafts cord then cloth."""
    g = game

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play Shepherd, Find a Sheep
    _choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    _play_card(g, "Desperate Shepherd")
    _activate_desperate_shepherd(g, True)
    _end_current_process(g)  # End Play
    _end_current_process(g)  # End Rest

    # Turn 2 (P2): no-op
    _end_current_process(g)
    _end_current_process(g)

    # Turn 3 (P1): Shear a sheep, deliver, find cord
    _choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    _play_card(g, "Seamstress")
    _ds_search_for_sheep(g)
    _ds_separate_ball_and_deliver_to_seamstress(g)
    _step_until_available(g, max_steps=60)
    _seamstress_find_cord(g)
    _step_until_available(g, max_steps=60)
    _end_current_process(g)
    _end_current_process(g)

    # Turn 4 (P2): no-op
    _end_current_process(g)
    _end_current_process(g)

    # Turn 5 (P1): Shear a sheep, deliver, find cord
    _ds_search_for_sheep(g)
    _ds_separate_ball_and_deliver_to_seamstress(g)
    _step_until_available(g, max_steps=60)
    _seamstress_find_cord(g)
    _step_until_available(g, max_steps=60)
    _end_current_process(g)
    _end_current_process(g)

    # Turn 6 (P2): no-op
    _end_current_process(g)
    _end_current_process(g)

    # Turn 7 (P1 / Seamstress): Find cloth
    _seamstress_find_cloth_from_two_cords(g)
    _step_until_available(g, max_steps=60)
    _end_current_process(g)
    _end_current_process(g)
