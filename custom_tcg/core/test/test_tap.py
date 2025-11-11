"""Test the tap action."""

from unittest.mock import Mock

import pytest

from custom_tcg.core.card.select import Select
from custom_tcg.core.card.tap import Tap
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.effect.activated import Activated
from custom_tcg.core.interface import ICard, IPlayer


@pytest.fixture
def mock_player() -> Mock:
    """Mock a player.

    :return: A mocked player.
    :rtype: Mock
    """
    return Mock(spec=IPlayer)


@pytest.fixture
def mock_card(mock_player: Mock) -> Mock:
    """Mock a card to test.

    :return: A mocked target card.
    :rtype: Mock
    """
    card = Mock(spec=ICard)
    card.name = "Test Card"
    card.player = mock_player
    return card


@pytest.fixture
def mock_target_card(mock_player: Mock) -> Mock:
    """Mock a target card to activate.

    :return: A mocked target card.
    :rtype: Mock
    """
    target_card = Mock(spec=ICard)
    target_card.name = "Test Target Card"
    target_card.player = mock_player
    return target_card


@pytest.fixture
def mock_context() -> Mock:
    """Mock an execution context.

    :return: A mocked execution context.
    :rtype: Mock
    """
    return Mock()


@pytest.fixture
def mock_select() -> Mock:
    """Mock a Select action.

    :return: A mocked Select action.
    :rtype: Mock
    """
    select = Mock(spec=Select)
    select.selected = []
    return select


def test_tap_constructor_single_card(
    mock_card: Mock,
    mock_player: Mock,
    mock_target_card: Mock,
) -> None:
    """Test constructor with single card.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_target_card: The mocked target card.
    :type mock_target_card: Mock
    """
    card_name = Mock()
    action = Tap(
        name=card_name,
        cards_to_activate=mock_target_card,
        card=mock_card,
        player=mock_player,
    )
    assert action.cards_to_activate is mock_target_card
    assert action.card is mock_card
    assert action.player is mock_player
    assert action.name is card_name
    assert len(action.selectors) == 0


def test_tap_constructor_list_of_cards(
    mock_card: Mock,
    mock_player: Mock,
) -> None:
    """Test constructor with list of cards.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    """
    cards = [Mock(), Mock(), Mock()]
    action = Tap(
        cards_to_activate=cards,  # pyright: ignore[reportArgumentType]
        card=mock_card,
        player=mock_player,
    )
    assert action.cards_to_activate == cards
    assert len(action.selectors) == 0


def test_tap_constructor_with_select(
    mock_card: Mock,
    mock_player: Mock,
    mock_select: Mock,
) -> None:
    """Test constructor with Select action.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_select: The mocked Select action.
    :type mock_select: Mock
    """
    action = Tap(
        cards_to_activate=mock_select,
        card=mock_card,
        player=mock_player,
    )
    assert action.cards_to_activate is mock_select
    assert mock_select in action.selectors


def test_tap_constructor_custom_name(
    mock_card: Mock,
    mock_player: Mock,
    mock_target_card: Mock,
) -> None:
    """Test constructor with custom name.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_target_card: The mocked target card.
    :type mock_target_card: Mock
    """
    action = Tap(
        cards_to_activate=mock_target_card,
        card=mock_card,
        player=mock_player,
        name="Custom Tap",
    )
    assert action.name == "Custom Tap"


def test_reset_state_with_select(
    mock_card: Mock,
    mock_player: Mock,
    mock_select: Mock,
) -> None:
    """Test reset state with Select action.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_select: The mocked Select action.
    :type mock_select: Mock
    """
    action = Tap(
        cards_to_activate=mock_select,
        card=mock_card,
        player=mock_player,
    )

    action.reset_state()

    mock_select.reset_state.assert_called_once()


def test_reset_state_without_select(
    mock_card: Mock,
    mock_player: Mock,
    mock_target_card: Mock,
) -> None:
    """Test reset state without Select action.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_target_card: The mocked target card.
    :type mock_target_card: Mock
    """
    action = Tap(
        cards_to_activate=mock_target_card,
        card=mock_card,
        player=mock_player,
    )

    action.reset_state()

    assert action.state == ActionStateDef.not_started


def test_enter_with_single_card(
    mock_card: Mock,
    mock_player: Mock,
    mock_target_card: Mock,
    mock_context: Mock,
) -> None:
    """Test enter with single card activates it.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_target_card: The mocked target card.
    :type mock_target_card: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    action = Tap(
        cards_to_activate=mock_target_card,
        card=mock_card,
        player=mock_player,
    )

    action.enter(context=mock_context)

    mock_context.execute.assert_called_once()
    call_args = mock_context.execute.call_args[1]
    executed_action = call_args["action"]
    assert executed_action.card == mock_card
    assert executed_action.player == mock_player
    assert executed_action.effect_to_add is Activated


def test_enter_with_list_of_cards(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
) -> None:
    """Test enter with list of cards activates all.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    cards = [Mock(), Mock(), Mock()]
    action = Tap(
        cards_to_activate=cards,  # pyright: ignore[reportArgumentType]
        card=mock_card,
        player=mock_player,
    )

    action.enter(context=mock_context)

    expected_calls = 3
    assert mock_context.execute.call_count == expected_calls


def test_enter_with_select(
    mock_card: Mock,
    mock_player: Mock,
    mock_select: Mock,
    mock_context: Mock,
) -> None:
    """Test enter with Select action uses selected cards.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_select: The mocked Select action.
    :type mock_select: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    selected_cards = [Mock(), Mock()]
    mock_select.selected = selected_cards

    action = Tap(
        cards_to_activate=mock_select,
        card=mock_card,
        player=mock_player,
    )

    action.enter(context=mock_context)

    expected_calls = 2
    assert mock_context.execute.call_count == expected_calls


def test_enter_with_empty_select(
    mock_card: Mock,
    mock_player: Mock,
    mock_select: Mock,
    mock_context: Mock,
) -> None:
    """Test enter with empty Select action.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_select: The mocked Select action.
    :type mock_select: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    mock_select.selected = []

    action = Tap(
        cards_to_activate=mock_select,
        card=mock_card,
        player=mock_player,
    )

    action.enter(context=mock_context)

    mock_context.execute.assert_not_called()
