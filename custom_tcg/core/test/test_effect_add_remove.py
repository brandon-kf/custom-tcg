"""Tests for adding and removing effects via actions."""

from unittest.mock import Mock

import pytest

from custom_tcg.core.dimension import EffectStateDef
from custom_tcg.core.effect.add_effect import AddEffect
from custom_tcg.core.effect.effect import Effect
from custom_tcg.core.effect.remove_effect import RemoveEffect
from custom_tcg.core.interface import ICard


@pytest.fixture
def mock_player() -> Mock:
    """Return a simple player mock."""
    return Mock(name="PlayerMock")


@pytest.fixture
def source_card() -> Mock:
    """Return a card mock used as the action's card (must support register)."""
    card = Mock(name="SourceCardMock", spec=ICard)
    card.effects = []
    card.register = Mock()
    return card


@pytest.fixture
def target_card(mock_player: Mock) -> Mock:
    """Return a card mock to receive an effect (with an effects list)."""
    card = Mock(name="TargetCardMock", spec=ICard)
    card.name = "Target"
    card.player = mock_player
    card.effects = []
    return card


@pytest.fixture
def mock_context() -> Mock:
    """Return a simple execution context mock."""
    return Mock(name="ExecutionContextMock")


def test_add_effect_appends_and_activates(
    mock_player: Mock,
    source_card: Mock,
    target_card: Mock,
    mock_context: Mock,
) -> None:
    """AddEffect should append a copy of the effect and activate it."""
    effect = Effect(name="Shiny", card=target_card)

    action = AddEffect(
        effect_to_add=effect,
        cards_affected=target_card,
        card=source_card,
        player=mock_player,
    )

    action.enter(context=mock_context)

    # Check that an Effect with the same name was added to target_card
    added_effects = [e for e in target_card.effects if isinstance(e, Effect)]
    assert len(added_effects) == 1
    added_effect = added_effects[0]
    assert added_effect.name == "Shiny"
    assert added_effect.state == EffectStateDef.active


def test_remove_effect_deactivates_and_removes(
    mock_player: Mock,
    source_card: Mock,
    target_card: Mock,
    mock_context: Mock,
) -> None:
    """RemoveEffect should deactivate the effect and remove it from the card."""
    effect = Effect(name="Glow", card=target_card)
    # Ensure the effect is present prior to removal
    target_card.effects.append(effect)
    effect.activate(context=mock_context)
    assert effect.state == EffectStateDef.active

    action = RemoveEffect(
        effect_to_remove=effect,
        card_to_remove_from=target_card,
        card=source_card,
        player=mock_player,
    )

    action.enter(context=mock_context)

    assert effect not in target_card.effects
    assert effect.state == EffectStateDef.inactive
