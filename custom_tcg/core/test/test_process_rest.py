"""Tests for `custom_tcg.core.process.rest` module."""

from unittest.mock import Mock

from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.effect.effect import Activated
from custom_tcg.core.process.rest import Rest


def test_rest_removes_activated_from_owned_beings() -> None:
    """Remove Activated effects from player's being cards in play."""
    player = Mock(name="PlayerMock")
    other = Mock(name="OtherPlayer")

    # Player card with Activated effect and being type
    owned_card = Mock(name="OwnedBeing")
    owned_card.types = [CardTypeDef.being]
    owned_card.effects = [Activated(card=owned_card)]

    # Other player's card should not be altered
    other_card = Mock(name="OtherBeing")
    other_card.types = [CardTypeDef.being]
    other_card.effects = [Activated(card=other_card)]

    player.played = [owned_card]
    other.played = [other_card]

    card = Mock(name="ProcessCard")
    card.register = Mock()

    rest = Rest(card=card, player=player)
    context = Mock(name="ExecutionContextMock")
    context.player = player

    rest.enter(context=context)

    assert owned_card.effects == []
    assert len(other_card.effects) == 1
