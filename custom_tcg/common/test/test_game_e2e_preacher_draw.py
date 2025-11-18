"""E2E: Resourceful Preacher draws a card by gifting two held items.

Flow overview:
- Turn 1 (P1): Play Resourceful Preacher.
- Turn 2 (P2): No-op.
- Turn 3 (P1): Play That Pebble Girl; Separate a Pebble and deliver it to
    Preacher.
- Turn 4 (P2): No-op.
- Turn 5 (P1): Use That Pebble Girl again; deliver a second Pebble.
  Then activate Resourceful Preacher to discard both Pebbles and draw 1 card.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.resourceful_preacher import ResourcefulPreacher
from custom_tcg.common.being.that_pebble_girl import ThatPebbleGirl
from custom_tcg.common.item.pebble import Pebble
from custom_tcg.common.util.e2e_test_beings import activate_that_pebble_girl
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
    step_until_available,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_preacher_draw(game: Game) -> None:
    """End-to-end: Resourceful Preacher discards items to draw a card."""
    g = game

    # Deck order: Draw pops last-first.
    # We want to draw Preacher, then That Pebble Girl, and still have one card
    # to draw from Preacher's activation (use a Pebble as a dummy top card).
    game.players[0].main_cards.extend(
        (
            Pebble.create(player=game.players[0]),
            ThatPebbleGirl.create(player=game.players[0]),
            ResourcefulPreacher.create(player=game.players[0]),
        ),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play Resourceful Preacher
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Resourceful Preacher")
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest

    # Turn 2 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 3 (P1): Play That Pebble Girl; separate+deliver a Pebble to Preacher
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "That Pebble Girl")
    activate_that_pebble_girl(
        g,
        separate=Pebble,
        deliver=("Resourceful Preacher", "Pebble"),
    )
    end_current_process(g)
    end_current_process(g)

    # Turn 4 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 5 (P1): Deliver second Pebble and activate Preacher to draw
    activate_that_pebble_girl(
        g,
        separate=Pebble,
        deliver=("Resourceful Preacher", "Pebble"),
    )

    hand_before = len(g.context.player.hand)
    # Activate Preacher - two Pebbles auto-selected (auto_n=True, exact match)
    choose_by_name_contains(g, "Activate from card 'Resourceful Preacher'")

    # Verify a single card was drawn
    step_until_available(g, max_steps=80)
    assert len(g.context.player.hand) == hand_before + 1, (
        "Expected hand size to increase by 1 from Preacher draw"
    )

    end_current_process(g)
    end_current_process(g)
