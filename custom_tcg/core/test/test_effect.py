"""Tests for core effect modules."""

from unittest.mock import Mock

import pytest

from custom_tcg.core.dimension import EffectStateDef
from custom_tcg.core.effect.effect import Activated, Effect


@pytest.fixture
def mock_player() -> Mock:
    """Provide a simple player mock."""
    return Mock(name="PlayerMock")


@pytest.fixture
def mock_card(mock_player: Mock) -> Mock:
    """Provide a simple card mock with a player attribute."""
    card = Mock(name="CardMock")
    card.player = mock_player
    card.effects = []
    return card


@pytest.fixture
def mock_context() -> Mock:
    """Return a simple execution context mock for these tests."""
    return Mock(name="ExecutionContextMock")


def test_effect_initial_state_and_properties(
    mock_card: Mock,
    mock_context: Mock,
) -> None:
    """Effect should initialize inactive with provided name/card/player."""
    eff = Effect(name="TestEffect", card=mock_card)

    assert eff.name == "TestEffect"
    assert eff.card is mock_card
    assert eff.player is mock_card.player
    assert eff.state == EffectStateDef.inactive
    assert eff.actions == []

    # Activate/deactivate toggles state
    eff.activate(context=mock_context)
    assert eff.state == EffectStateDef.active

    eff.deactivate(context=mock_context)
    assert eff.state == EffectStateDef.inactive


def test_effect_bind_deactivation_default(mock_card: Mock) -> None:
    """Default bind_deactivation returns False."""
    eff = Effect(name="Any", card=mock_card)
    assert eff.bind_deactivation(context=Mock()) is False


def test_activated_effect_name(mock_card: Mock) -> None:
    """Activated subclass should set a fixed name."""
    activated = Activated(card=mock_card)
    assert activated.name == "Activated"
    assert activated.card is mock_card
