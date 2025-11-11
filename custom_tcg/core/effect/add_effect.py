"""Add an effect."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from custom_tcg.core.action import Action
from custom_tcg.core.card.select import Select
from custom_tcg.core.interface import (
    ICard,
    IEffect,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        IExecutionContext,
        IPlayer,
    )


class AddEffect(Action):
    """Add an effect."""

    effect_to_add: IEffect | type[IEffect]
    cards_affected: ICard | list[ICard] | Select

    def __init__(  # noqa: PLR0913
        self: AddEffect,
        effect_to_add: IEffect | type[IEffect],
        cards_affected: ICard | list[ICard] | Select,
        card: ICard,
        player: IPlayer,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
    ) -> None:
        """Create an add effect action."""
        calculated_name: str = name or (
            effect_to_add.name
            if isinstance(effect_to_add, IEffect)
            else effect_to_add.__name__
        )
        super().__init__(
            name=calculated_name,
            card=card,
            player=player,
            bind=bind,
            costs=costs,
        )
        self.effect_to_add = effect_to_add
        self.cards_affected = cards_affected

        if isinstance(cards_affected, Select):
            self.selectors.append(cards_affected)

    @override
    def enter(self: AddEffect, context: IExecutionContext) -> None:
        super().enter(context=context)

        cards_affected: list[ICard]

        if isinstance(self.cards_affected, Select):
            cards_affected = cast("list[ICard]", self.cards_affected.selected)

        elif isinstance(self.cards_affected, ICard):
            cards_affected = [self.cards_affected]

        else:
            cards_affected = self.cards_affected

        for card in cards_affected:
            created_effect: IEffect = (
                self.effect_to_add.create(card=card)
                if isinstance(self.effect_to_add, type)
                else self.effect_to_add.copy(card=card)
            )
            created_effect.card_affecting = self.card
            created_effect.card_affected = card
            created_effect.activate(context=context)
