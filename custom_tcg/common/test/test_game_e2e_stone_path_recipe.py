"""E2E: Early Architect builds a Stone Path using Pile of Rocks.

Flow overview:
- Turn 1 (P1): Play Early Architect and That Pebble Girl. Collect a Pile of
    Rocks and deliver it to Early Architect.
- Turn 2 (P2): No-op.
- Turn 3 (P1): Collect a second Pile of Rocks and deliver it to Early
    Architect, then build a Stone Path (requires two piles, path is heavy and
    not held).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.early_architect import EarlyArchitect
from custom_tcg.common.being.that_pebble_girl import ThatPebbleGirl
from custom_tcg.common.effect.interface import IHeld
from custom_tcg.common.util.e2e_test_beings import (
    activate_early_architect,
    activate_that_pebble_girl,
)
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_stone_path_recipe(game: Game) -> None:
    """End-to-end: Early Architect builds a Stone Path from two rock piles."""
    g = game

    # Add required beings to main and re-setup ordering.
    # Append so Draw pops Early Architect first, then That Pebble Girl
    game.players[0].main_cards.extend(
        (
            EarlyArchitect.create(player=game.players[0]),
            ThatPebbleGirl.create(player=game.players[0]),
        ),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play Early Architect
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "That Pebble Girl")
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest

    # Turn 2 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 3 (P1): Play That Pebble Girl; collect and deliver first pile.
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Early Architect")
    activate_that_pebble_girl(g, deliver=("Early Architect", "Pile of Rocks"))
    end_current_process(g)
    end_current_process(g)

    # Turn 4 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 5 (P1): Collect and deliver second pile, then build Stone Path.
    activate_that_pebble_girl(g, deliver=("Early Architect", "Pile of Rocks"))
    # Verify Early Architect holds two piles now
    piles_held_by_ea = [
        c
        for c in g.context.player.played
        if c.name == "Pile of Rocks"
        for e in c.effects
        if isinstance(e, IHeld) and e.card_held_by.name == "Early Architect"
    ]
    required_piles = 2
    assert len(piles_held_by_ea) >= required_piles, (
        "Expected 2 Pile of Rocks held by Early Architect, found "
        f"{len(piles_held_by_ea)}"
    )
    activate_early_architect(g, build_stone_path=True)
    end_current_process(g)
    end_current_process(g)
