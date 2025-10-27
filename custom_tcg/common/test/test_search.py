"""Tests for `custom_tcg.common.action.search` module."""

from unittest.mock import Mock

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.search import Search
from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import ActionStateDef


def test_search_queues_find_when_success() -> None:
    """Queue the internal Find action when bind_success returns True."""
    player = Mock(name="PlayerMock")
    searcher = Card(name="Searcher", player=player, types=[], classes=[])

    # Dummy factory list is not used directly because we do not execute Find
    cards_to_search_for = []

    context = Mock(name="ExecutionContext")

    search = Search(
        searcher=searcher,
        cards_to_search_for=cards_to_search_for,
        bind_success=lambda ctx: True,  # noqa: ARG005
        card=searcher,
        player=player,
    )

    search.enter(context=context)

    # It should have attempted to execute the Find action and be queued
    assert context.execute.call_count == 1
    executed_action = context.execute.call_args.kwargs["action"]
    assert isinstance(executed_action, Find)
    assert search.state == ActionStateDef.queued


def test_search_cancels_when_bind_fails() -> None:
    """Cancel the search when bind_success returns False."""
    player = Mock(name="PlayerMock")
    searcher = Card(name="Searcher", player=player, types=[], classes=[])
    context = Mock(name="ExecutionContext")

    search = Search(
        searcher=searcher,
        cards_to_search_for=[],
        bind_success=lambda ctx: False,  # noqa: ARG005
        card=searcher,
        player=player,
    )

    search.enter(context=context)

    assert search.state == ActionStateDef.cancelled
    context.execute.assert_not_called()
