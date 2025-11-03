"""Tests for `custom_tcg.common.action.deliver` module."""

from unittest.mock import Mock

import pytest

from custom_tcg.common.action.deliver import Deliver
from custom_tcg.common.action.hold import Hold
from custom_tcg.common.card_type_def import CardTypeDef as CommonCardTypeDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.holding import Holding
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.anon import Player
from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import EffectStateDef
from custom_tcg.core.effect.remove_effect import RemoveEffect
from custom_tcg.core.execution.execution import ExecutionContext


@pytest.fixture
def player() -> Player:
    """Minimal test player suitable for behavior flows."""
    return Player(
        session_object_id="test-player",
        name="Test Player",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )


def _make_holder(player: Player, constitution: int = 10) -> Card:
    """Create a card that can hold items with given constitution."""
    holder = Card(name="Holder", player=player, types=[], classes=[])
    holder.effects.append(
        BeingStats(
            name="Base",
            card=holder,
            constitution=constitution,
            encumberance=0,
        ),
    )
    return holder


def _make_item(player: Player, name: str, heft: int = 1) -> Card:
    """Create an item card with given name and heft."""
    item = Card(name=name, player=player, types=[], classes=[])
    item.types.append(CommonCardTypeDef.item)
    item.effects.append(
        ItemStats(name="Stats", card=item, heft=heft),
    )
    return item


def test_hold_target_activation_creates_bidirectional_holding_effects(
    player: Player,
) -> None:
    """Test that HoldTarget activation creates Holding effects on both cards.

    This test verifies the new linkage system where HoldTarget manages the
    creation and linking of paired Holding effects. When a HoldTarget effect
    is activated, it should:
    1. Create a corresponding Holding effect on the holder card
    2. Establish proper bidirectional references between the effects
    3. Activate the Holding effect on the holder card
    """
    ctx = ExecutionContext(players=[player])

    holder = _make_holder(player, constitution=5)
    item = _make_item(player, name="TestItem", heft=2)

    # Create a Holding effect and add it to the item
    holding = Holding(card_held=item, card_holding=holder, card=holder)

    # Initially no effects should be active
    assert len([e for e in item.effects if isinstance(e, Holding)]) == 0
    assert len([e for e in holder.effects if isinstance(e, Holding)]) == 0

    # Activate the Holding effect using real execution context
    holding.activate(context=ctx)

    # Drain any pending actions from the execution context
    while ctx.ready:
        action = ctx.ready.pop(0)
        action.enter(context=ctx)

    # Verify both effects now exist and are properly linked
    item_hold_targets = [e for e in item.effects if isinstance(e, Holding)]
    holder_holdings = [e for e in holder.effects if isinstance(e, Holding)]

    assert len(item_hold_targets) == 1
    assert len(holder_holdings) == 1

    # Verify they reference the correct cards
    holding_effect = holder_holdings[0]
    held_effect = item_hold_targets[0]

    assert held_effect.card_holding is holder
    assert holding_effect.card_held is item
    assert holding_effect is held_effect

    # Verify the holding effect has expected properties
    assert holding_effect.name == f"Card '{holder.name}' holding '{item.name}'"

    # Verify that the Holding effect is activated
    assert holding_effect.state == EffectStateDef.active

    # Core functionality verified: bidirectional effects exist and are linked


def test_deliver_moves_held_items_to_receiver(player: Player) -> None:
    """Execute RemoveEffect then Hold for each selected item."""
    deliverer = _make_holder(player, constitution=10)
    receiver = _make_holder(player, constitution=10)

    # Two items currently held by deliverer
    item1 = _make_item(player, "Item1", heft=1)
    item2 = _make_item(player, "Item2", heft=1)

    # Set up initial holding relationships using the new system
    holding1 = Holding(card_held=item1, card_holding=deliverer, card=deliverer)
    holding2 = Holding(card_held=item2, card_holding=deliverer, card=deliverer)

    item1.effects.append(holding1)
    item2.effects.append(holding2)

    action = Deliver(
        card=deliverer,
        player=player,
        receiver=receiver,
        items=[item1, item2],
    )

    context = Mock(name="ExecutionContext")

    action.enter(context=context)

    # Expect two RemoveEffect followed by two Hold executions
    calls = [kw["action"] for _, kw in context.execute.call_args_list]

    remove_count = sum(isinstance(a, RemoveEffect) for a in calls)
    hold_count = sum(isinstance(a, Hold) for a in calls)

    expected_removals = 4  # For two items, remove effect from holder and item.
    expected_holds = 2  # One Hold per item to receiver.
    assert remove_count == expected_removals
    assert hold_count == expected_holds
