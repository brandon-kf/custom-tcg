"""Tests for Action class."""

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from custom_tcg.core.action import Action, ActionState
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.interface import ICard, IPlayer

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture
def card_mock() -> Mock:
    """Mock a card."""
    card = Mock(spec=ICard, name="CardMock")
    card.action_registry = []
    card.register = lambda action: card.action_registry.append(action)
    return card


@pytest.fixture
def player_mock() -> Mock:
    """Mock a player."""
    return Mock(spec=IPlayer, name="PlayerMock")


@pytest.fixture
def context_mock() -> Mock:
    """Mock an execution context."""
    return Mock(name="ExecutionContextMock")


def test_action_initialization_defaults(
    card_mock: Mock,
    player_mock: Mock,
) -> None:
    """Create an Action with default parameters."""
    action = Action(card=card_mock, player=player_mock)

    assert action.name == "Action"
    assert action.card is card_mock
    assert action.player is player_mock
    assert action.state == ActionStateDef.not_started
    assert action.bind is None
    assert action.notify == []
    assert action.selectors == []
    assert action.costs == []
    assert isinstance(action.session_object_id, str)
    assert action in card_mock.action_registry


def test_action_initialization_with_params(
    card_mock: Mock,
    player_mock: Mock,
) -> None:
    """Create an Action with specific parameters."""
    bind_fn: Callable[[tuple], bool] = lambda *_: True  # noqa: E731
    cost = Mock(name="CostAction")
    costs: list[Mock] = [cost]

    action = Action(
        card=card_mock,
        player=player_mock,
        state=ActionStateDef.stateless,
        bind=bind_fn,
        costs=costs,  # pyright: ignore[reportArgumentType]
        name="MyAction",
    )

    assert action.name == "MyAction"
    assert action.state == ActionStateDef.stateless
    assert action.bind is bind_fn
    assert action.costs is costs
    assert action in card_mock.action_registry


def test_action_initialization_invalid_state_raises(
    card_mock: Mock,
    player_mock: Mock,
) -> None:
    """Create an Action with invalid initial state for NotImplementedError."""
    with pytest.raises(expected_exception=NotImplementedError):
        Action(card=card_mock, player=player_mock, state=ActionStateDef.queued)


def test_change_state_updates(card_mock: Mock, player_mock: Mock) -> None:
    """Change state of action and verify update."""
    action = Action(card=card_mock, player=player_mock)
    action.change_state(state=ActionStateDef.entered)
    assert action.state == ActionStateDef.entered


def test_reset_state_sets_not_started(
    card_mock: Mock,
    player_mock: Mock,
    context_mock: Mock,
) -> None:
    """Reset state sets action state to not_started."""
    action = Action(card=card_mock, player=player_mock)
    action.queue(context=context_mock)
    assert action.state == ActionStateDef.queued
    action.reset_state()
    assert action.state == ActionStateDef.not_started


@pytest.mark.parametrize(
    argnames=("method", "expected_state"),
    argvalues=[
        ("queue", ActionStateDef.queued),
        ("enter", ActionStateDef.entered),
        ("request_input", ActionStateDef.input_requested),
        ("receive_input", ActionStateDef.input_received),
        ("complete", ActionStateDef.completed),
        ("cancel", ActionStateDef.cancelled),
    ],
)
def test_state_transitions(
    card_mock: Mock,
    player_mock: Mock,
    context_mock: Mock,
    method: str,
    expected_state: ActionState,
) -> None:
    """Test state transition methods change state appropriately."""
    action = Action(card=card_mock, player=player_mock)
    getattr(action, method)(context_mock)
    assert action.state == expected_state
