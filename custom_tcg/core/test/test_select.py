"""Test the select action."""

import sys
from unittest.mock import Mock

import pytest

from custom_tcg.core.card.select import Select


@pytest.fixture
def mock_player() -> Mock:
    """Mock a player.

    :return: A mocked player.
    :rtype: Mock
    """
    return Mock()


@pytest.fixture
def mock_card(mock_player: Mock) -> Mock:
    """Mock a card.

    :param mock_player: The mocked player.
    :type mock_player: Mock
    :return: A mocked card.
    :rtype: Mock
    """
    card = Mock()
    card.player = mock_player
    return card


@pytest.fixture
def mock_options() -> list[Mock]:
    """Mock a list of options.

    :return: A list of mocked options.
    :rtype: list[Mock]
    """
    option1 = Mock()
    option1.name = "Option1"
    option2 = Mock()
    option2.name = "Option2"
    option3 = Mock()
    option3.name = "Option3"
    return [option1, option2, option3]


@pytest.fixture
def mock_context(mock_player: Mock) -> Mock:
    """Mock an execution context.

    :param mock_player: The mocked player.
    :type mock_player: Mock
    :return: A mocked execution context.
    :rtype: Mock
    """
    context = Mock()
    context.player = mock_player
    return context


def test_select_constructor_with_list(
    mock_card: Mock,
    mock_player: Mock,
    mock_options: list[Mock],
) -> None:
    """Test constructor with list options.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        n=2,
        require_n=True,
        randomize=False,
    )
    assert select.name == "TestSelect"
    assert select.card is mock_card
    assert select.player is mock_player
    assert select.n == 2  # noqa: PLR2004
    assert select.require_n is True
    assert select.randomize is False
    assert select.options == []
    assert select.selected == []


def test_select_constructor_with_callable(
    mock_card: Mock,
    mock_player: Mock,
    mock_options: list[Mock],
) -> None:
    """Test constructor with callable options.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    options_callable = Mock(return_value=mock_options)
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=options_callable,
        n=1,
    )
    assert select.create_options is options_callable
    assert select.n == 1


def test_reset_state(mock_card: Mock, mock_player: Mock) -> None:
    """Test reset_state method.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=[],
    )
    select.options = [Mock(), Mock()]
    select.selected = [Mock()]

    select.reset_state()

    assert select.options == []
    assert select.selected == []


def test_queue_with_valid_options(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
    mock_options: list[Mock],
) -> None:
    """Test queue with valid options.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        n=2,
        require_n=True,
    )
    select.queue(context=mock_context)

    assert select.options == mock_options
    assert select.state.name != "Cancelled"


def test_queue_with_insufficient_options(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
) -> None:
    """Test queue with insufficient options when require_n is True.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    option = Mock()
    option.name = "OnlyOption"
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=[option],
        n=5,
        require_n=True,
    )
    select.queue(context=mock_context)

    assert select.state.name == "Cancelled"


def test_enter_without_randomize(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
    mock_options: list[Mock],
) -> None:
    """Test enter without randomization.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        n=2,
        randomize=False,
    )
    select.enter(context=mock_context)

    assert len(select.selected) == 2  # noqa: PLR2004
    assert select.selected == mock_options[:2]


def test_enter_with_randomize(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
    mock_options: list[Mock],
) -> None:
    """Test enter with randomization.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        n=2,
        randomize=True,
    )
    select.enter(context=mock_context)

    assert len(select.selected) == 2  # noqa: PLR2004
    # Can't assert exact order due to randomization


def test_speculate_with_require_n_true_sufficient_options(
    mock_card: Mock,
    mock_player: Mock,
    mock_options: list[Mock],
) -> None:
    """Test speculate with require_n True and sufficient options.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        n=2,
        require_n=True,
    )
    select.options = mock_options  # pyright: ignore[reportAttributeAccessIssue]

    assert select.speculate() is True


def test_speculate_with_require_n_true_insufficient_options(
    mock_card: Mock,
    mock_player: Mock,
) -> None:
    """Test speculate with require_n True and insufficient options.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    """
    option = Mock()
    option.name = "OnlyOption"
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=[option],
        n=5,
        require_n=True,
    )
    select.options = [option]

    assert select.speculate() is False


def test_speculate_with_require_n_false(
    mock_card: Mock,
    mock_player: Mock,
) -> None:
    """Test speculate with require_n False.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=[],
        n=5,
        require_n=False,
    )

    assert select.speculate() is True


def test_enter_with_more_options_than_n(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
    mock_options: list[Mock],
) -> None:
    """Test enter selects only n items when more options available.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        n=1,
        randomize=False,
    )
    select.enter(context=mock_context)

    assert len(select.selected) == 1
    assert select.selected[0] == mock_options[0]


def test_enter_with_fewer_options_than_n(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
) -> None:
    """Test enter selects all available items when fewer than n.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    option = Mock()
    option.name = "OnlyOption"
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=[option],
        n=5,
        randomize=False,
    )
    select.enter(context=mock_context)

    assert len(select.selected) == 1
    assert select.selected[0] == option


def test_queue_with_callable_options(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
    mock_options: list[Mock],
) -> None:
    """Test queue with callable options.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    options_callable = Mock(return_value=mock_options)
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=options_callable,
        n=2,
    )
    select.queue(context=mock_context)

    options_callable.assert_called_once_with(mock_context)
    assert select.options == mock_options


def test_enter_with_callable_options(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
    mock_options: list[Mock],
) -> None:
    """Test enter with callable options.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    options_callable = Mock(return_value=mock_options)
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=options_callable,
        n=2,
        randomize=False,
    )
    select.enter(context=mock_context)

    options_callable.assert_called_with(mock_context)
    assert select.selected == mock_options[:2]


def test_select_with_default_n_value(
    mock_card: Mock,
    mock_player: Mock,
    mock_options: list[Mock],
) -> None:
    """Test constructor with default n value (sys.maxsize).

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=mock_options,
    )
    assert select.n == sys.maxsize


def test_select_with_empty_options(
    mock_card: Mock,
    mock_player: Mock,
    mock_context: Mock,
) -> None:
    """Test select with empty options list.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    select = Select(
        name="TestSelect",
        card=mock_card,
        player=mock_player,
        options=[],
        n=1,
    )
    select.enter(context=mock_context)

    assert select.selected == []
