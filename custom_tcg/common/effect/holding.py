"""A holding effect."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.effect.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard, IExecutionContext


class Holding(Effect):
    """An effect showing that a card is holding another."""

    card_holding: ICard
    card_held: ICard

    def __init__(
        self: Holding,
        card: ICard,
        card_holding: ICard,
        card_held: ICard,
    ) -> None:
        """Create a holding effect."""
        super().__init__(
            name=f"Card '{card_holding.name}' holding '{card_held.name}'",
            card=card,
        )
        self.card_holding = card_holding
        self.card_held = card_held

    @classmethod
    def create(cls: type[Holding], card: ICard) -> Holding:
        """Create an instance of this effect."""
        raise NotImplementedError

    def copy(self: Holding, card: ICard) -> Holding:
        """Create an instance of this effect."""
        return self.__class__(
            card=card,
            card_holding=self.card_holding,
            card_held=card,
        )

    @override
    def activate(self: Holding, context: IExecutionContext) -> None:
        super().activate(context=context)

        if self not in self.card_holding.effects:
            self.card_holding.effects.append(self)

        if self not in self.card_held.effects:
            self.card_held.effects.append(self)

    @override
    def deactivate(self: Holding, context: IExecutionContext) -> None:
        super().deactivate(context=context)

        if self in self.card_holding.effects:
            self.card_holding.effects.remove(self)

        if self in self.card_held.effects:
            self.card_held.effects.remove(self)
