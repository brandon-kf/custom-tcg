"""Tests for `custom_tcg.common.action.deliver` module."""

from unittest.mock import Mock

from custom_tcg.common.action.deliver import Deliver
from custom_tcg.common.action.hold import Hold
from custom_tcg.common.effect.held import Held
from custom_tcg.core.card.card import Card
from custom_tcg.core.effect.remove_effect import RemoveEffect


def test_deliver_moves_held_items_to_receiver() -> None:
    """Execute RemoveEffect then Hold for each selected item."""
    player = Mock(name="PlayerMock")

    deliverer = Card(name="Deliverer", player=player, types=[], classes=[])
    receiver = Card(name="Receiver", player=player, types=[], classes=[])

    # Two items currently held by deliverer
    item1 = Card(name="Item1", player=player, types=[], classes=[])
    item2 = Card(name="Item2", player=player, types=[], classes=[])

    fake_holding = Mock(name="IHoldingMock")
    item1.effects.append(
        Held(
            card=item1,
            card_held_by=deliverer,
            card_holding_effect=fake_holding,
        ),
    )
    item2.effects.append(
        Held(
            card=item2,
            card_held_by=deliverer,
            card_holding_effect=fake_holding,
        ),
    )

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

    expected_per_type = 2
    assert remove_count == expected_per_type
    assert hold_count == expected_per_type
