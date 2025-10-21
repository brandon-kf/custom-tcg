"""Play a card."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action
from custom_tcg.core.dimension import CardTypeDef

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class Play(Action):
    """Play a card."""

    def __init__(
        self: Play,
        card: ICard,
        player: IPlayer,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create an activation."""
        super().__init__(
            name=f"Play '{card.name}'",
            player=player,
            card=card,
            bind=bind,
        )

    @override
    def enter(self: Play, context: IExecutionContext) -> None:
        super().enter(context=context)

        context.player.hand.remove(self.card)
        context.player.played.append(self.card)
        self.card.add_bindings(context=context)

        if CardTypeDef.process in self.card.types:
            context.player.processes.append(self.card)
