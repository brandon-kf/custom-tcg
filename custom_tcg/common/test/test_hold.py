"""Tests for `custom_tcg.common.action.hold` module."""

from unittest.mock import Mock

from custom_tcg.common.action.hold import Hold
from custom_tcg.common.card_type_def import CardTypeDef as CommonCardTypeDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.effect.add_effect import AddEffect


def _make_holder(player) -> Card:  # noqa: ANN001
    holder = Card(name="Holder", player=player, types=[], classes=[])
    # Give generous constitution to avoid overencumbrance in the happy path
    holder.effects.append(
        BeingStats(name="Base", card=holder, constitution=10, encumberance=0),
    )
    return holder


def _make_item(player, heft: int) -> Card:  # noqa: ANN001
    item = Card(name="Item", player=player, types=[], classes=[])
    # Mark as an item via ItemStats effect and heft as encumberance source
    item.types.append(CommonCardTypeDef.item)
    item.effects.append(
        ItemStats(name="It", card=item, heft=heft),
    )
    return item


def test_hold_executes_add_effect_when_not_overencumbered() -> None:
    """Execute AddEffect(Holding) when holder can support the item."""
    player = Mock(name="PlayerMock")

    holder = _make_holder(player)
    item = _make_item(player, heft=2)

    action = Hold(
        card_to_hold=item,
        card_holding=holder,
        card=holder,
        player=player,
    )

    context = Mock(name="ExecutionContext")

    action.enter(context=context)

    # Should execute an AddEffect targeting the holder
    assert context.execute.call_count == 1
    add = context.execute.call_args.kwargs["action"]
    assert isinstance(add, AddEffect)
    assert add.card_to_add_to is holder


def test_hold_does_not_execute_when_overencumbered() -> None:
    """Skip AddEffect if the item would overencumber the holder."""
    player = Mock(name="PlayerMock")

    holder = Card(name="WeakHolder", player=player, types=[], classes=[])
    # Constitution 1, already encumberance 0
    holder.effects.append(
        BeingStats(name="Weak", card=holder, constitution=1, encumberance=0),
    )
    # Item heft exceeds constitution
    item = _make_item(player, heft=5)

    action = Hold(
        card_to_hold=item,
        card_holding=holder,
        card=holder,
        player=player,
    )
    context = Mock(name="ExecutionContext")

    action.enter(context=context)

    context.execute.assert_not_called()
