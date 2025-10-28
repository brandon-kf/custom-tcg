"""Tests for `custom_tcg.core.execution.activate` module."""

from unittest.mock import Mock

from custom_tcg.core.card.tap import Tap
from custom_tcg.core.dimension import ActionStateDef, CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.resolve import Resolve


def test_activate_appends_to_notifications_when_not_process() -> None:
    """Append Tap and Resolve to notifications when card is not a process."""
    player = Mock(name="PlayerMock")
    # Action target list: these are existing actions to be resolved later
    a1 = Mock(name="A1")
    a1.name = "A1"
    a2 = Mock(name="A2")
    a2.name = "A2"

    card = Mock(name="CardMock")
    card.name = "CardX"
    card.types = []  # Not a process
    card.register = Mock()

    context = Mock(name="ContextMock")
    context.notifications = []
    context.ready = []
    context.process = Mock(name="ProcessPlaceholder")

    act = Activate(card=card, player=player, actions=[a1, a2])

    act.enter(context=context)

    # Should not change process and should append to notifications
    assert context.process is not card
    assert len(context.notifications) == 1 + 2  # Tap + two Resolve
    # All appended actions should be queued
    for added in context.notifications:
        assert added.state == ActionStateDef.queued

    # There should be exactly one Tap and it should target this card
    taps = [x for x in context.notifications if isinstance(x, Tap)]
    assert len(taps) == 1

    # There should be Resolves wrapping the provided actions
    resolves = [x for x in context.notifications if isinstance(x, Resolve)]
    assert {r.action for r in resolves} == {a1, a2}


def test_activate_sets_process_and_appends_to_ready_for_process_cards() -> None:
    """Set context.process and append to ready if the card is a process type."""
    player = Mock(name="PlayerMock")
    a = Mock(name="ActionToResolve")
    a.name = "ActionToResolve"

    card = Mock(name="ProcessCard")
    card.name = "Proc"
    card.types = [CardTypeDef.process]
    card.register = Mock()

    context = Mock(name="ContextMock")
    context.notifications = []
    context.ready = []
    context.process = Mock(name="ProcessPlaceholder")

    act = Activate(card=card, player=player, actions=[a])
    act.enter(context=context)

    assert context.process is card
    tap_and_one_resolve = 2  # Tap + Resolve
    assert len(context.ready) == tap_and_one_resolve
    assert all(x.state == ActionStateDef.queued for x in context.ready)
