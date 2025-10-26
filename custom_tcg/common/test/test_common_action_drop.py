"""Tests for `custom_tcg.common.action.drop` module."""

from unittest.mock import Mock

from custom_tcg.common.action.drop import Drop
from custom_tcg.common.effect.interface import IHeld
from custom_tcg.core.effect.remove_effect import RemoveEffect


def test_drop_removes_held_effect() -> None:
    """Execute a RemoveEffect for the IHeld effect on the target card."""
    player = Mock(name="PlayerMock")

    card = Mock(name="HolderCard")
    card.name = "Holder"
    card.player = player
    card.register = Mock()

    target = Mock(name="TargetCard")
    target.name = "Target"

    effect = Mock(spec=IHeld)
    effect.name = "HeldEffect"
    target.effects = [effect]

    context = Mock(name="ExecutionContext")

    action = Drop(card_to_drop=target, card=card, player=player)
    action.enter(context=context)

    # It should call execute once with a RemoveEffect action
    assert context.execute.call_count == 1
    remove = context.execute.call_args.kwargs["action"]

    assert isinstance(remove, RemoveEffect)
    assert remove.card_to_remove_from is target
