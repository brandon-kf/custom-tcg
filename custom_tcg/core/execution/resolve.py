"""Resolve an action."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class Resolve(Action):
    """Resolve an action."""

    action: IAction

    def __init__(
        self: Resolve,
        action: IAction,
        card: ICard,
        player: IPlayer,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create an activation."""
        super().__init__(
            name=f"Resolve from card '{card.name}' action '{action.name}'",
            card=card,
            player=player,
            bind=bind,
        )
        self.action = action

    @override
    def reset_state(self: Resolve) -> None:
        super().reset_state()

        self.action.reset_state()

    @override
    def enter(self: Resolve, context: IExecutionContext) -> None:
        super().enter(context=context)

        context.execute(action=self.action)
