"""Allow a card to drop another."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.common.effect.interface import IHeld
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

        held_effect: IHeld = next(
            effect
            for effect in self.card_to_drop.effects
            if isinstance(effect, IHeld)
        )

        context.execute(
            action=RemoveEffect(
                effect_to_remove=held_effect,
                card_to_remove_from=self.card_to_drop,
                card=self.card,
                player=self.player,
            ),
        )
