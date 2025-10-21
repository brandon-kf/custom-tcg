"""Remove an effect."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action

if TYPE_CHECKING:
    from custom_tcg.core.interface import (
        ICard,
        IEffect,
        IExecutionContext,
        IPlayer,
    )


class RemoveEffect(Action):
    """Remove an effect."""

    effect_to_remove: IEffect
    card_to_remove_from: ICard

    def __init__(  # noqa: PLR0913
        self: RemoveEffect,
        effect_to_remove: IEffect,
        card_to_remove_from: ICard,
        card: ICard,
        player: IPlayer,
        name: str | None = None,
    ) -> None:
        """Create a find action."""
        super().__init__(
            name=name
            or (
                f"Remove effect '{effect_to_remove.name}' "
                f"from '{card_to_remove_from.name}'"
            ),
            card=card,
            player=player,
        )
        self.effect_to_remove = effect_to_remove
        self.card_to_remove_from = card_to_remove_from

    @override
    def enter(self: RemoveEffect, context: IExecutionContext) -> None:
        super().enter(context=context)

        self.effect_to_remove.deactivate(context=context)
        self.card_to_remove_from.effects.remove(self.effect_to_remove)
