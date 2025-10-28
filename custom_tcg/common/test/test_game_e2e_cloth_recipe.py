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

from custom_tcg.common.player import DesperateShepherd, Seamstress
from custom_tcg.common.util.e2e_test_beings import (
    activate_desperate_shepherd,
    activate_seamstress,
)
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_cloth_recipe(game: Game) -> None:
    """End-to-end: Shepherd creates wool, Seamstress crafts cord then cloth."""
    g = game

    game.players[0].main_cards.extend(
        (
            Seamstress.create(player=game.players[0]),
            DesperateShepherd.create(player=game.players[0]),
        ),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play Shepherd, Find a Sheep
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Desperate Shepherd")
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest

    # Turn 2 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 3 (P1): Shear a sheep, deliver, find cord
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Seamstress")
    activate_desperate_shepherd(
        g,
        separate=True,
        deliver=("Seamstress", "Ball of Wool"),
    )
    activate_seamstress(g, find_cord=True)
    end_current_process(g)
    end_current_process(g)

    # Turn 4 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 5 (P1): Shear a sheep, deliver, find cord (second copy)
    activate_desperate_shepherd(
        g,
        separate=True,
        deliver=("Seamstress", "Ball of Wool"),
    )
    activate_seamstress(g, find_cord=True, find_cloth=True)
    end_current_process(g)
    end_current_process(g)
