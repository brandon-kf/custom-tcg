"""Tests for `custom_tcg.common.action.find` module."""

from __future__ import annotations

from unittest.mock import Mock

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.hold import Hold
from custom_tcg.common.card_type_def import CardTypeDef as CommonCardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card


class FoundItem(Card):
    """A simple item card factory used for Find tests."""

    @classmethod
    def create(cls, player) -> FoundItem:  # noqa: ANN001
        """Return a new item card with item stats."""
        card = FoundItem(name="Found", player=player, types=[], classes=[])
        # Mark as an item type and attach ItemStats for encumberance
        card.types.append(CommonCardTypeDef.item)
        card.effects.append(ItemStats(name="It", card=card, heft=1))
        return card


def test_find_creates_items_and_holds_with_finder() -> None:
    """Create N items from factories and queue Hold for each item."""
    player = Mock(name="PlayerMock")
    player.played = []

    finder = Card(name="Finder", player=player, types=[], classes=[])

    # Bind n to 2 for deterministic creation count
    def bind_n(context, factory) -> int:  # noqa: ANN001, ARG001
        return 2

    context = Mock(name="ExecutionContext")

    action = Find(
        finder=finder,
        cards_to_find=[FoundItem],
        card=finder,
        player=player,
        bind_n=bind_n,
    )

    action.enter(context=context)

    # Two items should be added to played, and two Hold executions queued
    expected = 2
    assert len(player.played) == expected

    hold_calls = [
        kw["action"]
        for _, kw in context.execute.call_args_list
        if isinstance(kw.get("action"), Hold)
    ]

    assert len(hold_calls) == expected
