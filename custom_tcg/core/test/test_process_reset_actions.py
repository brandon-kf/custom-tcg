"""Tests for `custom_tcg.core.process.reset_actions` module."""

from unittest.mock import Mock

from custom_tcg.core.process.reset_actions import ResetActions


def test_reset_actions_filters_and_resets() -> None:
    """Reset only actions matching the provided filter across played cards."""
    player = Mock(name="PlayerMock")
    other = Mock(name="OtherPlayer")

    # Create actions to be filtered
    a1 = Mock(name="A1")
    a2 = Mock(name="A2")
    a3 = Mock(name="A3")

    # Cards with actions collections
    c1 = Mock(name="Card1")
    c1.actions = [a1, a2]
    c1.register = Mock()
    c2 = Mock(name="Card2")
    c2.actions = [a3]
    c2.register = Mock()

    # Only player's played cards should be considered
    player.played = [c1]
    other.played = [c2]

    # Mark player attribute on actions' players to satisfy filter
    a1.player = player
    a2.player = player
    a3.player = other
    a1.card = c1
    a2.card = c1
    a3.card = c2

    # Filter: only reset a2
    def filter_actions(action) -> bool:  # noqa: ANN001
        return action is a2

    card = Mock(name="ProcessCard")
    card.register = Mock()

    ra = ResetActions(card=card, player=player, filter_actions=filter_actions)

    context = Mock(name="ExecutionContextMock")
    context.players = [player, other]

    ra.enter(context=context)

    a2.reset_state.assert_called_once_with()
    a1.reset_state.assert_not_called()
    a3.reset_state.assert_not_called()
