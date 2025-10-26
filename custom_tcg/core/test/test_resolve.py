"""Tests for `custom_tcg.core.execution.resolve` module."""

from unittest.mock import Mock

from custom_tcg.core.execution.resolve import Resolve


def test_resolve_enter_calls_context_execute() -> None:
    """Ensure Resolve.enter delegates to context.execute with wrapped action."""
    # Prepare a minimal action to be wrapped and a card/player for init
    wrapped_action = Mock(name="WrappedAction")
    wrapped_action.name = "DoSomething"
    # Card must support register() since Action.__init__ calls it
    card = Mock(name="CardMock")
    card.name = "CardA"
    card.register = Mock()
    player = Mock(name="PlayerMock")

    context = Mock(name="ExecutionContextMock")

    resolver = Resolve(action=wrapped_action, card=card, player=player)

    resolver.enter(context=context)

    context.execute.assert_called_once_with(action=wrapped_action)


def test_resolve_reset_state_propagates() -> None:
    """Ensure Resolve.reset_state calls reset on the wrapped action."""
    wrapped_action = Mock(name="WrappedAction")
    wrapped_action.name = "OtherAction"
    card = Mock(name="CardMock")
    card.name = "CardB"
    card.register = Mock()
    player = Mock(name="PlayerMock")

    resolver = Resolve(action=wrapped_action, card=card, player=player)

    resolver.reset_state()

    wrapped_action.reset_state.assert_called_once_with()
