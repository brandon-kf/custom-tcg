"""Test the draw action."""

from unittest.mock import Mock

import pytest

from custom_tcg.core.card.draw import Draw


@pytest.fixture
def mock_player() -> Mock:
    """Mock a player.

    :return: A mocked player.
    :rtype: Mock
    """
    player = Mock()
    player.hand = []
    player.main_cards = [Mock(), Mock()]  # Mocking a deck with two cards
    return player


@pytest.fixture
def mock_card(mock_player: Mock) -> Mock:
    """Mock a card.

    :return: A mocked card.
    :rtype: Mock
    """
    card = Mock()
    card.player = mock_player
    return card


@pytest.fixture
def draw_action(mock_card: Mock, mock_player: Mock) -> Draw:
    """Mock a draw action.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :return: A mocked draw action.
    :rtype: Draw
    """
    return Draw(n=2, card=mock_card, player=mock_player)


def test_draw_constructor(mock_card: Mock, mock_player: Mock) -> None:
    """Test constructor.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    """
    action = Draw(n=3, card=mock_card, player=mock_player)
    assert action._n == 3  # noqa: PLR2004, SLF001
    assert action.card is mock_card
    assert action.player is mock_player


def test_enter_draws_cards(draw_action: Draw, mock_player: Mock) -> None:
    """Test enter draws cards.

    :param draw_action: The draw action.
    :type draw_action: Draw
    :param mock_player: The mocked player.
    :type mock_player: Mock
    """
    draw_action.enter(context=Mock(player=mock_player))
    assert (
        len(mock_player.hand) == 2  # noqa: PLR2004
    )  # Two cards should be drawn
    assert len(mock_player.main_cards) == 0  # Deck should be empty after draw
