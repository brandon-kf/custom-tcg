"""Activate a card without honoring any of its effects."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from custom_tcg.core.action import Action
from custom_tcg.core.card.select import Select
from custom_tcg.core.effect.add_effect import AddEffect
from custom_tcg.core.effect.effect import Activated
from custom_tcg.core.interface import (
    ICard,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        IExecutionContext,
        IPlayer,
    )


class Tap(Action):
    """Activate a card without honoring any of its effects."""

    cards_to_activate: ICard | list[ICard] | Select

    def __init__(
        self: Tap,
        cards_to_activate: ICard | list[ICard] | Select,
        card: ICard,
        player: IPlayer,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create a tap cards action."""
        super().__init__(
            name=name or "Tap card(s)",
            card=card,
            player=player,
            bind=bind,
        )

        self.cards_to_activate = cards_to_activate

        if isinstance(cards_to_activate, Select):
            self.selectors.append(cards_to_activate)

    @override
    def enter(self: Tap, context: IExecutionContext) -> None:
        super().enter(context=context)

        cards: list[ICard]

        if isinstance(self.cards_to_activate, Select):
            cards = cast(
                "list[ICard]",
                self.cards_to_activate.selected,
            )

        elif isinstance(self.cards_to_activate, list):
            cards = self.cards_to_activate

        elif isinstance(self.cards_to_activate, ICard):
            cards = [self.cards_to_activate]

        else:
            raise TypeError

        for card in cards:
            context.execute(
                action=AddEffect(
                    effect_to_add=Activated(card=card),
                    cards_affected=card,
                    card=self.card,
                    player=self.player,
                ),
            )
