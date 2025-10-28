"""E2E: Destructive Darryl starts a Fire using unheld Flint and Pile of Wood.

Flow overview:
- Play Flint and Pile of Wood as items so they are found but not held.
- Later, play Destructive Darryl.
- On the next Play process for the same player, his bound activation evaluates
  automatically and consumes the unheld Flint and Pile of Wood to create Fire.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.destructive_darryl import DestructiveDarryl
from custom_tcg.common.item.flint import Flint
from custom_tcg.common.item.pile_of_wood import PileOfWood
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_fire_recipe(game: Game) -> None:
    """End-to-end: Destructive Darryl creates Fire from unheld items."""
    g = game

    # Deck order: Draw pops last-first, so append in reverse desired draw order.
    # We want to draw Flint, Flint, Pile of Wood, Pile of Wood, then Darryl.
    game.players[0].main_cards.extend(
        (
            DestructiveDarryl.create(player=game.players[0]),
            PileOfWood.create(player=game.players[0]),
            Flint.create(player=game.players[0]),
        ),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play Flint (unheld since played directly, not found)
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Flint")
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest

    # Turn 2 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 3 (P1): Play Pile of Wood (first copy)
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Pile of Wood")
    end_current_process(g)
    end_current_process(g)

    # Turn 4 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 5 (P1): Play Destructive Darryl
    # (His activation won't run until the next Play process.)
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Destructive Darryl")
    end_current_process(g)
    end_current_process(g)

    # Turn 6 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 7 (P1): Enter Play; trigger Darryl's activation (bound to Play).
    fire_cards = [c for c in g.context.player.played if c.name == "Fire"]
    assert fire_cards, "Expected a Fire to be created by Destructive Darryl"
    held_effects = [
        e for e in fire_cards[0].effects if hasattr(e, "card_held_by")
    ]
    assert not held_effects, "Fire should not be held after creation"

    # End Play + Rest for completeness
    end_current_process(g)
    end_current_process(g)
