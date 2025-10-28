"""E2E: Aimless Wanderer discovers a Trail by discarding a Stick.

Flow overview:
- Turn 1 (P1): Play Aimless Wanderer, separate a Stick from a held Pile of Wood.
- Turn 2 (P2): No-op.
- Turn 3 (P1): Discover a Trail by discarding the held Stick. The Trail is too
  heavy to be held (heft=1000), so it should be present in play and unheld.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.aimless_wanderer import AimlessWanderer
from custom_tcg.common.util.e2e_test_beings import activate_aimless_wanderer
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_trail_recipe(game: Game) -> None:
    """End-to-end: Aimless Wanderer creates a Stick, then discovers a Trail."""
    g = game

    game.players[0].main_cards.append(
        AimlessWanderer.create(player=game.players[0]),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Same-turn flow on P1: create Stick, then discover Trail within
    # one activation.
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Aimless Wanderer")
    activate_aimless_wanderer(g, find_stick=True, find_trail=True)
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest
