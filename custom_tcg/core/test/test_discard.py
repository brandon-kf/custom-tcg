"""Test the discard action."""

from unittest.mock import Mock

import pytest

from custom_tcg.core.card.discard import Discard


@pytest.fixture
def mock_card() -> Mock:
    """Mock a card.

    :return: A mocked card.
    :rtype: Mock
    """
    card = Mock()
    card.effects = [Mock(), Mock()]
    card.player = Mock()
    card.player.hand = [card]
    card.player.played = [card]
    return card


@pytest.fixture
def mock_player() -> Mock:
    """Mock a player.

    :return: A mocked player.
    :rtype: Mock
    """
    player = Mock()
    player.hand = []
    player.played = []
    return player


@pytest.fixture
def mock_select(mock_card: Mock) -> Mock:
    """Mock a card selection.

    :param mock_card: The mocked card to select.
    :type mock_card: Mock
    :return: A mocked card selection.
    :rtype: Mock
    """
    select = Mock()
    select.selected = [mock_card]
    select.reset_state = Mock()
    return select


@pytest.fixture
def discard_action(
    mock_select: Mock,
    mock_card: Mock,
    mock_player: Mock,
) -> Discard:
    """Mock a discard action.

    :param mock_select: The mocked card selection.
    :type mock_select: Mock
    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :return: A mocked discard action.
    :rtype: Discard
    """
    return Discard(
        cards_to_discard=mock_select,
        card=mock_card,
        player=mock_player,
        name="Test Discard",
        bind=None,
    )


def test_discard_constructor(
    mock_select: Mock,
    mock_card: Mock,
    mock_player: Mock,
) -> None:
    """Test constructor.

    :param mock_select: The mocked card selection.
    :type mock_select: Mock
    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    """
    action = Discard(
        cards_to_discard=mock_select,
        card=mock_card,
        player=mock_player,
    )
    assert action.cards_to_discard is mock_select
    assert mock_select in action.selectors


def test_reset_state_calls(discard_action: Discard, mock_select: Mock) -> None:
    """Test reset_state calls.

    :param discard_action: The discard action.
    :type discard_action: Discard
    :param mock_select: The mocked card selection.
    :type mock_select: Mock
    """
    discard_action.reset_state()
    mock_select.reset_state.assert_called_once()


def test_enter_removes_and_deactivates(
    discard_action: Discard,
    mock_card: Mock,
) -> None:
    """Test enter removes and deactivates.

    :param discard_action: The discard action.
    :type discard_action: Discard
    :param mock_card: The mocked card.
    :type mock_card: Mock
    """
    context = Mock()
    # Ensure card is in hand and played
    mock_card.player.hand = [mock_card]
    mock_card.player.played = [mock_card]
    # Effects
    for effect in mock_card.effects:
        effect.deactivate = Mock()
    discard_action.enter(context=context)
    assert mock_card not in mock_card.player.hand
    assert mock_card not in mock_card.player.played
    for effect in mock_card.effects:
        effect.deactivate.assert_called_once_with(context=context)


def test_enter_effect_deactivation_silent_failure(
    discard_action: Discard,
    mock_card: Mock,
) -> None:
    """Test enter effect deactivation silent failure.

    :param discard_action: The discard action.
    :type discard_action: Discard
    :param mock_card: The mocked card.
    :type mock_card: Mock
    """
    context = Mock()
    mock_card.player.hand = []
    mock_card.player.played = []
    for effect in mock_card.effects:
        effect.deactivate = Mock()
    discard_action.enter(context=context)
    for effect in mock_card.effects:
        effect.deactivate.assert_called_once_with(context=context)
