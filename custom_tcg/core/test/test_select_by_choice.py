"""Test the select by choice action."""

from unittest.mock import Mock

import pytest

from custom_tcg.core.card.select_by_choice import (
    SelectByChoice,
    SelectByChoiceOption,
)
from custom_tcg.core.dimension import ActionStateDef


@pytest.fixture
def mock_card() -> Mock:
    """Mock a card.

    :return: A mocked card.
    :rtype: Mock
    """
    return Mock()


@pytest.fixture
def mock_player() -> Mock:
    """Mock a player.

    :return: A mocked player.
    :rtype: Mock
    """
    return Mock()


@pytest.fixture
def mock_options() -> list[Mock]:
    """Mock options.

    :return: A list of mocked options.
    :rtype: list[Mock]
    """
    option1 = Mock()
    option1.name = "Option 1"
    option2 = Mock()
    option2.name = "Option 2"
    option3 = Mock()
    option3.name = "Option 3"
    return [option1, option2, option3]


@pytest.fixture
def select_by_choice(
    mock_card: Mock,
    mock_player: Mock,
    mock_options: list[Mock],
) -> SelectByChoice:
    """Create a select by choice action.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    :return: A select by choice action.
    :rtype: SelectByChoice
    """
    return SelectByChoice(
        name="Test Select",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        require_n=True,
        accept_n=2,
    )


@pytest.fixture
def mock_context() -> Mock:
    """Mock an execution context.

    :return: A mocked execution context.
    :rtype: Mock
    """
    context = Mock()
    context.choices = []
    return context


def test_select_by_choice_constructor(
    mock_card: Mock,
    mock_player: Mock,
    mock_options: list[Mock],
) -> None:
    """Test constructor with int accept_n.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    action = SelectByChoice(
        name="Test Select",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        require_n=True,
        accept_n=2,
    )
    assert action.name == "Test Select"
    assert action.card is mock_card
    assert action.player is mock_player
    assert action.accept_n == [2]
    assert action.require_n is True
    assert action.choice_actions == []


def test_select_by_choice_constructor_list_accept_n(
    mock_card: Mock,
    mock_player: Mock,
    mock_options: list[Mock],
) -> None:
    """Test constructor with list accept_n.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    action = SelectByChoice(
        name="Test Select",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        require_n=False,
        accept_n=[1, 2, 3],
    )
    assert action.accept_n == [1, 2, 3]
    assert action.require_n is False


def test_reset_state(select_by_choice: SelectByChoice) -> None:
    """Test reset state.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    """
    select_by_choice.confirm_action.state = ActionStateDef.completed
    select_by_choice.cancel_action.state = ActionStateDef.completed
    select_by_choice.choice_actions = [Mock(), Mock()]

    select_by_choice.reset_state()

    assert select_by_choice.confirm_action.state == ActionStateDef.not_started
    assert select_by_choice.cancel_action.state == ActionStateDef.not_started
    assert select_by_choice.choice_actions == []


def test_speculate_true(
    select_by_choice: SelectByChoice,
    mock_options: list[Mock],
) -> None:
    """Test speculate returns true when enough options.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select_by_choice.options = mock_options  # pyright: ignore[reportAttributeAccessIssue]
    assert select_by_choice.speculate() is True


def test_speculate_false(select_by_choice: SelectByChoice) -> None:
    """Test speculate returns false when not enough options.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    """
    select_by_choice.options = []
    assert select_by_choice.speculate() is False


def test_enter(
    select_by_choice: SelectByChoice,
    mock_context: Mock,
) -> None:
    """Test enter creates choice actions.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    :param mock_context: The mocked context.
    :type mock_context: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    """
    select_by_choice.enter(context=mock_context)

    expected_len = 4  # 3 options + confirm

    assert len(select_by_choice.choice_actions) == expected_len
    assert select_by_choice.state == ActionStateDef.input_requested
    assert mock_context.choices == select_by_choice.choice_actions


def test_enter_with_cancel(
    mock_card: Mock,
    mock_player: Mock,
    mock_options: list[Mock],
    mock_context: Mock,
) -> None:
    """Test enter includes cancel when not required.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param mock_options: The mocked options.
    :type mock_options: list[Mock]
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    action = SelectByChoice(
        name="Test Select",
        card=mock_card,
        player=mock_player,
        options=mock_options,
        require_n=False,
        accept_n=2,
    )

    action.enter(context=mock_context)

    expected_len = 5  # 3 options + confirm + cancel

    assert len(action.choice_actions) == expected_len


def test_receive_input_completed(
    select_by_choice: SelectByChoice,
    mock_context: Mock,
) -> None:
    """Test receive input completes when criteria satisfied.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    select_by_choice.selected = [Mock(), Mock()]
    select_by_choice.confirm_action.state = ActionStateDef.completed

    select_by_choice.receive_input(context=mock_context)

    assert select_by_choice.state == ActionStateDef.completed


def test_receive_input_not_enough_selected(
    select_by_choice: SelectByChoice,
    mock_context: Mock,
) -> None:
    """Test receive input resets when not enough selected.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    select_by_choice.selected = [Mock()]
    select_by_choice.confirm_action.state = ActionStateDef.completed
    select_by_choice.choice_actions = [Mock(), Mock()]

    select_by_choice.receive_input(context=mock_context)

    assert select_by_choice.confirm_action.state == ActionStateDef.not_started
    assert select_by_choice.state == ActionStateDef.input_requested
    assert mock_context.choices == select_by_choice.choice_actions


def test_receive_input_cancelled(
    select_by_choice: SelectByChoice,
    mock_context: Mock,
) -> None:
    """Test receive input cancels when cancel action completed.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    select_by_choice.cancel_action.state = ActionStateDef.completed

    select_by_choice.receive_input(context=mock_context)

    assert select_by_choice.state == ActionStateDef.cancelled


def test_complete(select_by_choice: SelectByChoice, mock_context: Mock) -> None:
    """Test complete clears choices.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    mock_context.choices = [Mock(), Mock()]

    select_by_choice.complete(context=mock_context)

    assert mock_context.choices == []


def test_cancel(select_by_choice: SelectByChoice, mock_context: Mock) -> None:
    """Test cancel clears choices.

    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    mock_context.choices = [Mock(), Mock()]

    select_by_choice.cancel(context=mock_context)

    assert mock_context.choices == []


def test_select_by_choice_option_constructor(
    mock_card: Mock,
    mock_player: Mock,
    select_by_choice: SelectByChoice,
) -> None:
    """Test SelectByChoiceOption constructor.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    """
    selected = Mock()
    selected.name = "Test Option"

    option = SelectByChoiceOption(
        name="Select 'Test Option'",
        selected=selected,
        selector=select_by_choice,
        card=mock_card,
        player=mock_player,
    )

    assert option.name == "Select 'Test Option'"
    assert option.selected is selected
    assert option.selector is select_by_choice
    assert option.card is mock_card
    assert option.player is mock_player


def test_select_by_choice_option_enter(
    mock_card: Mock,
    mock_player: Mock,
    select_by_choice: SelectByChoice,
    mock_context: Mock,
) -> None:
    """Test SelectByChoiceOption enter adds selection.

    :param mock_card: The mocked card.
    :type mock_card: Mock
    :param mock_player: The mocked player.
    :type mock_player: Mock
    :param select_by_choice: The select by choice action.
    :type select_by_choice: SelectByChoice
    :param mock_context: The mocked context.
    :type mock_context: Mock
    """
    selected = Mock()
    selected.name = "Test Option"
    select_by_choice.n = 0

    option = SelectByChoiceOption(
        name="Select 'Test Option'",
        selected=selected,
        selector=select_by_choice,
        card=mock_card,
        player=mock_player,
    )

    option.enter(context=mock_context)

    assert selected in select_by_choice.selected
    assert select_by_choice.n == 1
