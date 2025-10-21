"""Add an effect."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IEffect,
        IExecutionContext,
        IPlayer,
    )


class AddEffect(Action):
    """Add an effect."""

    effect_to_add: IEffect
    card_to_add_to: ICard

    def __init__(  # noqa: PLR0913
        self: AddEffect,
        effect_to_add: IEffect,
        card_to_add_to: ICard,
        card: ICard,
        player: IPlayer,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
    ) -> None:
        """Create a find action."""
        super().__init__(
            name=name
            or (
                f"Add effect '{effect_to_add.name}' "
                f"to '{card_to_add_to.name}'"
            ),
            card=card,
            player=player,
            bind=bind,
            costs=costs,
        )
        self.effect_to_add = effect_to_add
        self.card_to_add_to = card_to_add_to

    @override
    def enter(self: AddEffect, context: IExecutionContext) -> None:
        super().enter(context=context)

        self.card_to_add_to.effects.append(self.effect_to_add)
        self.effect_to_add.activate(context=context)
