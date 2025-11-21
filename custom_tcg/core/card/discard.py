"""Discard cards."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from custom_tcg.core.action import Action

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.card.select import Select
    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class Discard(Action):
    """Discard cards."""

    cards_to_discard: Select

    def __init__(
        self: Discard,
        cards_to_discard: Select,
        card: ICard,
        player: IPlayer,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create a discard cards action."""
        super().__init__(
            name=name or "Discard cards",
            card=card,
            player=player,
            bind=bind,
        )

        self.cards_to_discard = cards_to_discard

        self.selectors.append(cards_to_discard)

    @override
    def enter(self: Discard, context: IExecutionContext) -> None:
        super().enter(context=context)

        cards: list[ICard] = cast("list[ICard]", self.cards_to_discard.selected)

        for card in cards:
            if card in card.player.hand:
                card.player.hand.remove(card)
                card.player.discard.append(card)

            if card in card.player.played:
                card.player.played.remove(card)
                card.player.discard.append(card)

            for effect in card.effects:
                effect.deactivate(context=context)
