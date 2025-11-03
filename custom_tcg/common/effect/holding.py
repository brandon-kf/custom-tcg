"""A holding effect."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.common.action.drop import Drop
from custom_tcg.core.dimension import EffectStateDef
from custom_tcg.core.effect.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard, IExecutionContext


class Holding(Effect):
    """An effect showing that a card is holding another."""

    card_holding: ICard
    card_held: ICard
    drop: Drop

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
        self.drop = Drop(
            card_to_drop=card_holding,
            card=card,
            player=card.player,
        )
        self.actions.append(self.drop)

    @classmethod
    def create(cls: type[Holding], card: ICard) -> Holding:
        """Create an instance of this effect."""
        raise NotImplementedError

    def copy(self: Holding, card: ICard) -> Holding:
        """Create an instance of this effect."""
        return self.__class__(
            card=card,
            card_holding=self.card_holding,
            card_held=self.card_held,
        )

    @override
    def activate(self: Holding, context: IExecutionContext) -> None:
        super().activate(context=context)

        self.card_holding.actions.append(self.drop)

    @override
    def deactivate(self: Holding, context: IExecutionContext) -> None:
        # This will get called twice, once for holder and once for held.
        # Only evaluate the deactivation once.
        if self.state is EffectStateDef.active:
            super().deactivate(context=context)

            self.card_holding.actions.remove(self.drop)
