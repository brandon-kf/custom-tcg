"""Tests for `custom_tcg.common.action.select_by_held` module."""

from unittest.mock import Mock

from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.effect.hold_target import HoldTarget
from custom_tcg.core.card.card import Card


def test_select_by_held_filters_items_by_holder() -> None:
    """Return only items held by the selecting card, of the requested type."""
    player = Mock(name="PlayerMock")

    holder = Card(name="Holder", player=player, types=[], classes=[])

    # Two items, only one is held by holder
    item1 = Card(name="Item1", player=player, types=[], classes=[])
    item2 = Card(name="Item2", player=player, types=[], classes=[])

    # Fake an IHolding with a simple Mock; Held only stores it
    fake_holding = Mock(name="IHoldingMock")

    # Attach Held effect to item2 indicating it's held by 'holder'
    item2.effects.append(
        HoldTarget(
            card=item2,
            card_held_by=holder,
            card_holding_effect=fake_holding,
        ),
    )

    player.played = [item1, item2]

    selector = SelectByHeld(
        name="Select held items",
        card=holder,
        player=player,
        held_type=Card,  # require items to be Card instances
        require_n=False,
        accept_n=1,
    )

    context = Mock(name="ExecutionContextMock")
    context.player = player

    # Build options via Select.queue() path
    selector.queue(context=context)

    # Only item2 should appear (it's Card and held by holder)
    assert selector.options == [item2]
