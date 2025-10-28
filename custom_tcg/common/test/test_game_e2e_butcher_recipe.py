"""E2E: Questionable Butcher butchers a Peasant for rations and pelt.

Flow overview:
- Turn 1 (P1): Play Questionable Butcher.
- Same turn: Activate Butcher, select Peasant to butcher; verify Extra Rations
  and Pelt are created and held by the Butcher.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.peasant import Peasant
from custom_tcg.common.being.questionable_butcher import QuestionableButcher
from custom_tcg.common.util.e2e_test_beings import activate_questionable_butcher
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_butcher_recipe(game: Game) -> None:
    """End-to-end: Butcher consumes Peasant; yields Extra Rations and Pelt."""
    g = game

    # Add required being to main and re-setup ordering.
    game.players[0].main_cards.append(
        QuestionableButcher.create(player=game.players[0]),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Draw and play Butcher, then activate and butcher Peasant.
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Questionable Butcher")
    activate_questionable_butcher(g, chop_chop=Peasant)
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest
