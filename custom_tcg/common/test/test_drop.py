"""Tests for `custom_tcg.common.action.drop` module."""

from unittest.mock import Mock

from custom_tcg.common.action.drop import Drop
from custom_tcg.common.effect.holding import Holding
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

    effect = Mock(spec=Holding)
    effect.name = "HeldEffect"
    effect.card_holding = Mock()
    effect.card_held = target
    target.effects = [effect]

    context = Mock(name="ExecutionContext")

    action = Drop(card_to_drop=target, card=card, player=player)
    action.enter(context=context)

    # Two RemoveEffect actions should execute for holder and held.
    assert context.execute.call_count == 2  # noqa: PLR2004
    remove = context.execute.call_args.kwargs["action"]

    assert isinstance(remove, RemoveEffect)
    assert remove.card_to_remove_from is target
