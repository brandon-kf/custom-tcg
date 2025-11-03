"""Allow a card to drop another."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.common.effect.holding import Holding
from custom_tcg.core.action import Action
from custom_tcg.core.effect.remove_effect import RemoveEffect

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class Drop(Action):
    """Allow a card to drop another."""

    card_to_drop: ICard

    def __init__(
        self: Drop,
        card_to_drop: ICard,
        card: ICard,
        player: IPlayer,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create a drop action."""
        super().__init__(
            name=f"'{card.name}' drops '{card_to_drop.name}'",
            card=card,
            player=player,
            bind=bind,
        )
        self.card_to_drop = card_to_drop

    @override
    def enter(self: Drop, context: IExecutionContext) -> None:
        super().enter(context=context)

        holding_effect: Holding = next(
            effect
            for effect in self.card_to_drop.effects
            if isinstance(effect, Holding)
        )

        # Remove effect from holder.
        context.execute(
            action=RemoveEffect(
                effect_to_remove=holding_effect,
                card_to_remove_from=holding_effect.card_holding,
                card=self.card,
                player=self.player,
            ),
        )

        # Remove effect from held.
        context.execute(
            action=RemoveEffect(
                effect_to_remove=holding_effect,
                card_to_remove_from=holding_effect.card_held,
                card=self.card,
                player=self.player,
            ),
        )
