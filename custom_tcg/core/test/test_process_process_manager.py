"""Tests for `custom_tcg.core.process.process_manager` module."""

from unittest.mock import Mock

from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.process.process_manager import ProcessManager


def test_process_manager_initializes_and_adds_actions() -> None:
    """Create ProcessManager and ensure it adds helper actions to the card."""
    player = Mock(name="PlayerMock")
    card = Mock(name="CardMock")
    card.register = Mock()
    card.actions = []

    pm = ProcessManager(name="Mgr", card=card, player=player)

    # Both helper actions should be added to the card
    assert pm.end_process in card.actions
    assert pm.reset_actions in card.actions


def test_process_manager_enter_transitions_to_input_requested() -> None:
    """Enter should set state to input_requested when no notifications."""
    player = Mock(name="PlayerMock")
    card = Mock(name="CardMock")
    card.register = Mock()
    card.actions = []

    pm = ProcessManager(name="Mgr", card=card, player=player)

    context = Mock(name="ExecutionContextMock")
    context.notifications = []
    context.ready = []
    context.choices = []

    pm.enter(context=context)

    assert pm.state == ActionStateDef.input_requested
    assert context.choices == [pm.end_process]


def test_process_manager_complete_executes_reset_actions() -> None:
    """Complete should clear choices and execute reset_actions."""
    player = Mock(name="PlayerMock")
    card = Mock(name="CardMock")
    card.register = Mock()
    card.actions = []

    pm = ProcessManager(name="Mgr", card=card, player=player)
    context = Mock(name="ExecutionContextMock")
    context.notifications = []
    context.ready = []
    context.choices = [pm.end_process]

    pm.complete(context=context)

    assert context.choices == []
    context.execute.assert_called_once_with(action=pm.reset_actions)


def test_process_manager_moves_notifications_to_ready() -> None:
    """Move queued notifications into ready and clear notifications list."""
    player = Mock(name="PlayerMock")
    card = Mock(name="CardMock")
    card.register = Mock()
    card.actions = []

    pm = ProcessManager(name="Mgr", card=card, player=player)
    context = Mock(name="ExecutionContextMock")
    notification = Mock(name="NotifAction")
    context.notifications = [notification]
    context.ready = []

    pm.update_next_state(context=context)

    assert notification in context.ready
    assert context.notifications == []
    assert notification.state == ActionStateDef.queued
    assert pm.state == ActionStateDef.queued
