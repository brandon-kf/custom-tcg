"""E2E: Apprentice Smith smelts Metal using Pile of Rocks delivered.

Flow overview:
- Turn 1 (P1): Play Apprentice Smith.
- Turn 2 (P2): No-op.
- Turn 3 (P1): Play That Pebble Girl; collect and deliver first Pile of Rocks
  to Apprentice Smith.
- Turn 4 (P2): No-op.
- Turn 5 (P1): Use That Pebble Girl again; deliver second Pile of Rocks, then
  activate Apprentice Smith to smelt Metal (discard 2 piles).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.apprentice_smith import ApprenticeSmith
from custom_tcg.common.being.that_pebble_girl import ThatPebbleGirl
from custom_tcg.common.util.e2e_test_beings import (
    activate_apprentice_smith,
    activate_that_pebble_girl,
)
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_metal_recipe(game: Game) -> None:
    """End-to-end: Apprentice Smith smelts Metal from rocks."""
    g = game

    # Add required beings to main and re-setup ordering.
    # Order so Draw pops Apprentice Smith first, then That Pebble Girl
    game.players[0].main_cards.extend(
        (
            ThatPebbleGirl.create(player=game.players[0]),
            ApprenticeSmith.create(player=game.players[0]),
        ),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play Apprentice Smith
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Apprentice Smith")
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest

    # Turn 2 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 3 (P1): Play That Pebble Girl; deliver first Pile of Rocks
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "That Pebble Girl")
    activate_that_pebble_girl(
        g,
        deliver=("Apprentice Smith", "Pile of Rocks"),
    )
    end_current_process(g)
    end_current_process(g)

    # Turn 4 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 5 (P1): Deliver second Pile of Rocks and smelt Metal
    activate_that_pebble_girl(
        g,
        deliver=("Apprentice Smith", "Pile of Rocks"),
    )
    activate_apprentice_smith(g, smelt_metal=True)
    end_current_process(g)
    end_current_process(g)
