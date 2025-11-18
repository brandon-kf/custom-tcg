"""E2E: Test SelectByChoice speculate function branches with ResourcefulPreacher.

This test exercises different branches of the SelectByChoice.speculate() method:
1. Exact acceptance criteria met (len(options) == accept_n[0]) - auto-select
2. Options identical with sufficient count - auto-select when all same
3. Different options but insufficient count - speculation fails
4. More options than needed with identical items - auto-select

Flow overview:
- Setup ResourcefulPreacher with different held item combinations
- Activate to trigger SelectByChoice with auto_n=True
- Verify auto-selection behavior in each scenario
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.being.resourceful_preacher import ResourcefulPreacher
from custom_tcg.common.effect.holding import Holding
from custom_tcg.common.item.stick import Stick
from custom_tcg.common.item.stone import Stone
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    end_current_process,
    play_card,
    step_until_available,
)

if TYPE_CHECKING:
    from custom_tcg.core.game import Game


def test_select_by_choice_speculate_exact_match(game: Game) -> None:
    """Test auto-selection when options exactly match accept_n."""
    g = game

    # Add ResourcefulPreacher and extra cards to deck for drawing
    preacher = ResourcefulPreacher.create(player=game.players[0])
    stick1 = Stick.create(player=game.players[0])
    stick2 = Stick.create(player=game.players[0])

    # Add extra cards to main deck so Draw action has cards to draw
    extra_card1 = Stick.create(player=game.players[0])
    extra_card2 = Stone.create(player=game.players[0])

    game.players[0].main_cards.extend([extra_card2, extra_card1, preacher])
    game.players[0].played.extend([stick1, stick2])

    # Make preacher hold both sticks before game start
    preacher.effects.extend(
        [
            Holding(card=preacher, card_holding=preacher, card_held=stick1),
            Holding(card=preacher, card_holding=preacher, card_held=stick2),
        ]
    )

    game.setup()
    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play ResourcefulPreacher
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

    # Turn 3 (P1): Activate ResourcefulPreacher - should auto-select both sticks
    choose_by_name_contains(g, "Activate from card 'Resourceful Preacher'")

    # Verify auto-selection happened (no choices should be presented)
    step_until_available(g, max_steps=60)

    # Verify both sticks were discarded and a card was drawn
    remaining_sticks = [c for c in g.context.player.played if c.name == "Stick"]
    assert len(remaining_sticks) == 0, (
        f"Expected 0 sticks remaining, found {len(remaining_sticks)}"
    )

    # Verify a card was drawn
    assert len(g.context.player.hand) >= 1, (
        "Expected at least 1 card in hand after draw"
    )

    end_current_process(g)
    end_current_process(g)


def test_select_by_choice_speculate_different_options(game: Game) -> None:
    """Test auto-selection when option count matches accept_n."""
    g = game

    # Add ResourcefulPreacher, one Stick, and one Stone to deck
    preacher = ResourcefulPreacher.create(player=game.players[0])
    stick = Stick.create(player=game.players[0])
    stone = Stone.create(player=game.players[0])

    # Add extra cards to main deck so Draw action has cards to draw
    extra_card1 = Stick.create(player=game.players[0])
    extra_card2 = Stone.create(player=game.players[0])

    game.players[0].main_cards.extend([extra_card2, extra_card1, preacher])
    game.players[0].played.extend([stick, stone])

    # Make preacher hold both items (different types) before game start
    preacher.effects.extend(
        [
            Holding(card=preacher, card_holding=preacher, card_held=stick),
            Holding(card=preacher, card_holding=preacher, card_held=stone),
        ]
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play ResourcefulPreacher
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

    # Turn 3 (P1): Activate ResourcefulPreacher - should auto-select both items
    # since we have exactly 2 options and need exactly 2
    choose_by_name_contains(g, "Activate from card 'Resourceful Preacher'")

    # Verify auto-selection happened (no choices should be presented)
    step_until_available(g, max_steps=60)

    # Verify both items were discarded and a card was drawn
    remaining_items = [
        c for c in g.context.player.played if c.name in ["Stick", "Stone"]
    ]
    assert len(remaining_items) == 0, (
        "Expected both items to be selected and discarded"
    )

    assert len(g.context.player.hand) >= 1, "Expected a card to be drawn"

    end_current_process(g)
    end_current_process(g)


def test_select_by_choice_speculate_insufficient_options(game: Game) -> None:
    """Test speculation failure when insufficient options available."""
    g = game

    # Add ResourcefulPreacher with only one item (needs 2)
    preacher = ResourcefulPreacher.create(player=game.players[0])
    stick = Stick.create(player=game.players[0])

    # Add extra cards to main deck so Draw action has cards to draw
    extra_card1 = Stick.create(player=game.players[0])
    extra_card2 = Stone.create(player=game.players[0])

    game.players[0].main_cards.extend([extra_card2, extra_card1, preacher])
    game.players[0].played.extend([stick])

    # Make preacher hold only one item before game start
    preacher.effects.extend(
        [
            Holding(card=preacher, card_holding=preacher, card_held=stick),
        ]
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play ResourcefulPreacher
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

    # Turn 3 (P1): Try to activate ResourcefulPreacher
    # Should fail/cancel due to insufficient items
    choose_by_name_contains(g, "Activate from card 'Resourceful Preacher'")

    # Should not be able to complete the action
    step_until_available(g, max_steps=60)

    # Verify no items were discarded and no card was drawn
    # (action should have been cancelled)
    remaining_stick = [c for c in g.context.player.played if c.name == "Stick"]
    assert len(remaining_stick) == 1, (
        "Expected stick to remain since action should be cancelled"
    )

    end_current_process(g)
    end_current_process(g)


def test_select_by_choice_speculate_three_identical_options(game: Game) -> None:
    """Test auto-selection when there are more options than needed."""
    g = game

    # Add ResourcefulPreacher with three identical Sticks (needs 2)
    preacher = ResourcefulPreacher.create(player=game.players[0])
    stick1 = Stick.create(player=game.players[0])
    stick2 = Stick.create(player=game.players[0])
    stick3 = Stick.create(player=game.players[0])

    # Add extra cards to main deck so Draw action has cards to draw
    extra_card1 = Stick.create(player=game.players[0])
    extra_card2 = Stone.create(player=game.players[0])

    game.players[0].main_cards.extend([extra_card2, extra_card1, preacher])
    game.players[0].played.extend([stick1, stick2, stick3])

    # Make preacher hold all three sticks before game start
    preacher.effects.extend(
        [
            Holding(card=preacher, card_holding=preacher, card_held=stick1),
            Holding(card=preacher, card_holding=preacher, card_held=stick2),
            Holding(card=preacher, card_holding=preacher, card_held=stick3),
        ]
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play ResourcefulPreacher
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

    # Turn 3 (P1): Activate ResourcefulPreacher
    # Should auto-select 2 of the 3 identical sticks
    choose_by_name_contains(g, "Activate from card 'Resourceful Preacher'")

    # Should auto-select since all options are identical
    step_until_available(g, max_steps=60)

    # Verify exactly 2 sticks were discarded and 1 remains
    remaining_sticks = [c for c in g.context.player.played if c.name == "Stick"]
    assert len(remaining_sticks) == 1, (
        "Expected 1 stick to remain after auto-selecting 2"
    )

    assert len(g.context.player.hand) >= 1, "Expected a card to be drawn"

    end_current_process(g)
    end_current_process(g)


def test_select_by_choice_speculate_more_different_options(game: Game) -> None:
    """Test manual selection when more different options than needed."""
    g = game

    # Add ResourcefulPreacher with three different items (needs 2)
    preacher = ResourcefulPreacher.create(player=game.players[0])
    stick = Stick.create(player=game.players[0])
    stone1 = Stone.create(player=game.players[0])
    stone2 = Stone.create(player=game.players[0])

    # Add extra cards to main deck so Draw action has cards to draw
    extra_card1 = Stick.create(player=game.players[0])
    extra_card2 = Stone.create(player=game.players[0])

    game.players[0].main_cards.extend([extra_card2, extra_card1, preacher])
    game.players[0].played.extend([stick, stone1, stone2])

    # Make preacher hold all three items before game start
    preacher.effects.extend(
        [
            Holding(card=preacher, card_holding=preacher, card_held=stick),
            Holding(card=preacher, card_holding=preacher, card_held=stone1),
            Holding(card=preacher, card_holding=preacher, card_held=stone2),
        ]
    )

    game.setup()

    choices = g.start()
    assert choices, "Expected initial choices from first process activation"

    # Turn 1 (P1): Play ResourcefulPreacher
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

    # Turn 3 (P1): Activate ResourcefulPreacher - should NOT auto-select
    # since we have more than needed and they're different
    choose_by_name_contains(g, "Activate from card 'Resourceful Preacher'")

    # Should present choices since we have too many different options
    # First select Stick
    stick_choice = next(
        (c for c in g.context.choices if "Stick" in c.name),
        None,
    )
    assert stick_choice is not None, "Expected to find Stick choice"
    g.choose(stick_choice)

    # Then select first Stone
    stone_choice = next(
        (c for c in g.context.choices if "Stone" in c.name),
        None,
    )
    assert stone_choice is not None, "Expected to find Stone choice"
    g.choose(stone_choice)

    # Finally confirm the selection
    confirm_choice = next(
        (c for c in g.context.choices if c.name == "Confirm"),
        None,
    )
    assert confirm_choice is not None, "Expected to find Confirm choice"
    g.choose(confirm_choice)

    step_until_available(g, max_steps=60)

    # Verify 2 items were discarded and a card was drawn
    remaining_items = [
        c for c in g.context.player.played if c.name in ["Stick", "Stone"]
    ]
    assert len(remaining_items) == 1, (
        "Expected one item to remain since we selected only 2 out of 3"
    )

    assert len(g.context.player.hand) >= 1, "Expected a card to be drawn"

    end_current_process(g)
    end_current_process(g)
