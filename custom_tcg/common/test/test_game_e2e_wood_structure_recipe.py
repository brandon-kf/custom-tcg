"""E2E: Apprentice Carpenter constructs a Wood Structure using Pile of Wood.

Flow overview:
- Turn 1 (P1): Play Apprentice Carpenter.
- Turn 2 (P2): No-op.
- Turn 3 (P1): Play Aimless Wanderer; collect and deliver first Pile of Wood
  to Apprentice Carpenter.
- Turn 4 (P2): No-op.
- Turn 5 (P1): Use Aimless Wanderer again; deliver second Pile of Wood, then
  activate Apprentice Carpenter to construct a Wood Structure (discard 2 piles).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.aimless_wanderer import AimlessWanderer
from custom_tcg.common.being.apprentice_carpenter import ApprenticeCarpenter
from custom_tcg.common.util.e2e_test_beings import (
    activate_aimless_wanderer,
    activate_apprentice_carpenter,
)
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_wood_structure_recipe(game: Game) -> None:
    """End-to-end: Apprentice Carpenter constructs a Wood Structure."""
    g = game

    # Add required beings to main and re-setup ordering.
    # Order so Draw pops Apprentice Carpenter first, then Aimless Wanderer
    game.players[0].main_cards.extend(
        (
            AimlessWanderer.create(player=game.players[0]),
            ApprenticeCarpenter.create(player=game.players[0]),
        ),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play Apprentice Carpenter
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Apprentice Carpenter")
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest

    # Turn 2 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 3 (P1): Play Aimless Wanderer; deliver first Pile of Wood
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Aimless Wanderer")
    activate_aimless_wanderer(
        g,
        deliver=("Apprentice Carpenter", "Pile of Wood"),
    )
    end_current_process(g)
    end_current_process(g)

    # Turn 4 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 5 (P1): Deliver second Pile of Wood and construct a Wood Structure
    activate_aimless_wanderer(
        g,
        deliver=("Apprentice Carpenter", "Pile of Wood"),
    )
    activate_apprentice_carpenter(g, build_wood_structure=True)
    end_current_process(g)
    end_current_process(g)
