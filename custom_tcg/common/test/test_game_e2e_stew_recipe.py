"""E2E: The Stewmaker cooks a Stew from two held food items.

Flow overview:
- Turn 1 (P1): Play The Stewmaker (receiver for deliveries).
- Turn 2 (P2): No-op.
- Turn 3 (P1): Play Questionable Butcher.
- Turn 4 (P2): No-op.
- Turn 5 (P1): Play a sacrificial being (e.g., Aimless Wanderer); butcher it
    to create Extra Rations, then deliver those rations to The Stewmaker.
- Turn 6 (P2): No-op.
- Turn 7 (P1): Play another sacrificial being (e.g., Seamstress); butcher and
    deliver a second Extra Rations to The Stewmaker.
- Turn 9 (P1): Activate The Stewmaker; choose Stew, then discard two held
    Extra Rations to create a Stew.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.aimless_wanderer import AimlessWanderer
from custom_tcg.common.being.questionable_butcher import QuestionableButcher
from custom_tcg.common.being.seamstress import Seamstress
from custom_tcg.common.being.the_stewmaker import TheStewmaker
from custom_tcg.common.util.e2e_test_beings import IHeld
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    choose_option_n_then_confirm,
    choose_option_then_confirm,
    end_current_process,
    play_card,
    step_until_available,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_stew_recipe(game: Game) -> None:
    """End-to-end: The Stewmaker cooks a Stew from Extra Rations."""
    g = game

    # Deck order: Draw pops last-first. We want to draw The Stewmaker, then
    # Questionable Butcher, then Aimless Wanderer, then Seamstress.
    game.players[0].main_cards.extend(
        (
            Seamstress.create(player=game.players[0]),
            AimlessWanderer.create(player=game.players[0]),
            QuestionableButcher.create(player=game.players[0]),
            TheStewmaker.create(player=game.players[0]),
        ),
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play The Stewmaker
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "The Stewmaker")
    end_current_process(g)  # End Play
    end_current_process(g)  # End Rest

    # Turn 2 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 3 (P1): Play Questionable Butcher
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Questionable Butcher")
    end_current_process(g)
    end_current_process(g)

    # Turn 4 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 5 (P1): Play sacrificial being; butcher and deliver rations
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Aimless Wanderer")
    # Activate Butcher: choose target being, then deliver Extra Rations
    choose_by_name_contains(g, "Activate from card 'Questionable Butcher'")
    assert choose_option_then_confirm(
        g,
        "Select 'Aimless Wanderer'",
        max_steps=60,
    ), "Expected to select 'Aimless Wanderer' to butcher and confirm"
    # Deliver to The Stewmaker
    assert choose_option_then_confirm(
        g,
        "Select 'The Stewmaker'",
        max_steps=60,
    ), "Expected to select 'The Stewmaker' as receiver and confirm"
    assert choose_option_then_confirm(
        g,
        "Select 'Extra Rations'",
        max_steps=60,
    ), "Expected to select 'Extra Rations' to deliver and confirm"
    end_current_process(g)
    end_current_process(g)

    # Turn 6 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 7 (P1): Play second sacrificial being; butcher and deliver again
    choose_by_name_contains(
        g,
        "Activate from card 'Peasant' action(s): 'Draw 1 card'",
    )
    play_card(g, "Seamstress")
    choose_by_name_contains(g, "Activate from card 'Questionable Butcher'")
    assert choose_option_then_confirm(
        g,
        "Select 'Seamstress'",
        max_steps=60,
    ), "Expected to select 'Seamstress' to butcher and confirm"
    assert choose_option_then_confirm(
        g,
        "Select 'The Stewmaker'",
        max_steps=60,
    ), "Expected to select 'The Stewmaker' as receiver and confirm"
    assert choose_option_then_confirm(
        g,
        "Select 'Extra Rations'",
        max_steps=60,
    ), "Expected to select 'Extra Rations' to deliver and confirm"
    end_current_process(g)
    end_current_process(g)

    # Turn 8 (P2): no-op
    end_current_process(g)
    end_current_process(g)

    # Turn 9 (P1): Activate and cook Stew using held rations
    choose_by_name_contains(g, "Activate from card 'The Stewmaker'")
    assert choose_option_then_confirm(
        g,
        "Select 'Stew'",
        max_steps=60,
    ), "Expected to select 'Stew' and confirm"
    assert choose_option_n_then_confirm(
        g,
        "Select 'Extra Rations'",
        2,
        max_steps=80,
    ), "Expected to select two held 'Extra Rations' to discard and confirm"

    # Verify a Stew exists and is held by The Stewmaker.
    step_until_available(g, max_steps=60)
    stew_cards = [c for c in g.context.player.played if c.name == "Stew"]
    assert stew_cards, "Expected a Stew to be created by The Stewmaker"
    held = next(
        (e for e in stew_cards[0].effects if isinstance(e, IHeld)),
        None,
    )
    assert held is not None
    assert held.card_held_by.name == "The Stewmaker"

    end_current_process(g)
    end_current_process(g)
