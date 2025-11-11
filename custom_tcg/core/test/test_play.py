"""Tests for `custom_tcg.core.execution.play` module."""

from unittest.mock import Mock

from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.play import Play


def test_play_moves_card_and_adds_bindings() -> None:
    """Remove the card from hand, place it in played, and add bindings."""
    player = Mock(name="PlayerMock")
    player.hand = []
    player.played = []
    player.processes = []

    card = Mock(name="CardMock")
    card.name = "BasicCard"
    card.types = []
    card.effects = []
    card.register = Mock()
    card.add_bindings = Mock()

    player.hand.append(card)

    context = Mock(name="ExecutionContextMock")
    context.player = player

    play = Play(card=card, player=player)
    play.enter(context=context)

    assert card not in player.hand
    assert card in player.played
    card.add_bindings.assert_called_once()
    assert card not in player.processes


def test_play_adds_to_processes_for_process_cards() -> None:
    """Append the card to player.processes if it has the process type."""
    player = Mock(name="PlayerMock")
    player.hand = []
    player.played = []
    player.processes = []

    card = Mock(name="ProcessCard")
    card.name = "ProcCard"
    card.types = [CardTypeDef.process]
    card.effects = []
    card.register = Mock()
    card.add_bindings = Mock()

    player.hand.append(card)

    context = Mock(name="ExecutionContextMock")
    context.player = player

    play = Play(card=card, player=player)
    play.enter(context=context)

    assert card in player.played
    assert card in player.processes
