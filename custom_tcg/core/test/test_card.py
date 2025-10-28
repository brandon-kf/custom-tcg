"""Tests for the Card class in the core module."""

from typing import Any
from unittest.mock import Mock

import pytest

from custom_tcg.core.card.card import Card


@pytest.fixture
def mock_player() -> Mock:
    """Mock a player."""
    return Mock(name="PlayerMock")


@pytest.fixture
def mock_action() -> Mock:
    """Mock an action."""
    action = Mock(name="ActionMock")
    action.card = Mock(name="CardOwnerMock")
    action.player = Mock(name="PlayerMock")
    action.bind = None
    action.notify = []
    return action


@pytest.fixture
def mock_type() -> Mock:
    """Mock a card type."""
    return Mock(name="CardType")


@pytest.fixture
def mock_class() -> Mock:
    """Mock a card class."""
    return Mock(name="CardClass")


@pytest.fixture
def card(
    mock_player: Mock,
    mock_action: Mock,
    mock_type: Mock,
    mock_class: Mock,
) -> Card:
    """Return a basic Card instance with one registered action."""
    return Card(
        name="Test Card",
        player=mock_player,
        types=[mock_type],
        classes=[mock_class],
        actions=[mock_action],
    )


def test_card_initialization(
    card: Card,
    mock_player: Mock,
    mock_action: Mock,
    mock_type: Mock,
    mock_class: Mock,
) -> None:
    """Ensure constructor correctly initializes fields."""
    assert card.name == "Test Card"
    assert card.player is mock_player
    assert mock_type in card.types
    assert mock_class in card.classes
    assert card.actions == [mock_action]
    assert card.effects == []
    assert isinstance(card.session_object_id, str)
    assert card.action_registry == []


def test_register_adds_action(card: Card, mock_action: Mock) -> None:
    """register() should add an action to the action_registry."""
    card.register(action=mock_action)
    assert mock_action in card.action_registry


def test_add_binding_success(card: Card) -> None:
    """add_binding() should append notify when bind returns True."""
    existing = Mock(name="ExistingAction")
    entering = Mock(name="EnteringAction")
    existing.notify = []
    entering.notify = []

    existing.bind = lambda *_: True
    entering.bind = lambda *_: True

    card.add_binding(existing=existing, entering=entering)

    assert existing in entering.notify
    assert entering in existing.notify


def test_add_binding_one_sided(card: Card) -> None:
    """If only one bind returns True, only that side gets notified."""
    existing = Mock()
    entering = Mock()
    existing.notify = []
    entering.notify = []

    existing.bind = lambda *_: True
    entering.bind = lambda *_: False

    card.add_binding(existing=existing, entering=entering)

    assert existing in entering.notify
    assert entering not in existing.notify


def test_remove_binding_success(card: Card) -> None:
    """remove_binding() should remove notify references if bind returns True."""
    existing = Mock()
    exiting = Mock()
    existing.bind = lambda *_: True
    exiting.bind = lambda *_: True

    existing.notify = [exiting]
    exiting.notify = [existing]

    card.remove_binding(existing=existing, exiting=exiting)

    assert exiting not in existing.notify
    assert existing not in exiting.notify


def test_map_binding_operation_applies(card: Card) -> None:
    """Test map_binding_operation calls for all eligible pairs."""
    # Create mock context with one other player and one played card
    other_action = Mock()
    other_card = Mock()
    other_card.action_registry = [other_action]
    other_player = Mock()
    other_player.played = [other_card]

    context = Mock()
    context.players = [other_player]

    operation = Mock()

    # Register one entering action
    card_action = Mock()
    card.action_registry = [card_action]

    card.map_binding_operation(context, operation)

    operation.assert_called_once_with(other_action, card_action)


def test_add_bindings_delegates(card: Card) -> None:
    """Test add_bindings delegate to map_binding_operation."""
    called: dict[str, Any] = {}

    def fake_map_binding_operation(context, operation) -> None:  # noqa: ANN001, ARG001
        called["func"] = operation

    card.map_binding_operation = fake_map_binding_operation
    context = Mock()

    card.add_bindings(context=context)

    assert called["func"] == card.add_binding


def test_remove_bindings_delegates(card: Card) -> None:
    """Test remove_bindings should delegate to map_binding_operation."""
    called: dict[str, Any] = {}

    def fake_map_binding_operation(context, operation) -> None:  # noqa: ANN001, ARG001
        called["func"] = operation

    card.map_binding_operation = fake_map_binding_operation
    context = Mock()

    card.remove_bindings(context=context)

    assert called["func"] == card.remove_binding


def test_create_not_implemented() -> None:
    """Card.create should raise NotImplementedError."""
    with pytest.raises(expected_exception=NotImplementedError):
        Card.create(player=Mock())
