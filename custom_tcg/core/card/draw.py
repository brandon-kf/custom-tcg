"""Draw cards."""

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


class Draw(Action):
    """Draw cards."""

    _n: int

    def __init__(  # noqa: PLR0913
        self: Draw,
        n: int,
        card: ICard,
        player: IPlayer,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
    ) -> None:
        """Create a draw action."""
        super().__init__(
            name=name or f"Draw {n} {'card' if n == 1 else 'cards'}",
            card=card,
            player=player,
            bind=bind,
            costs=costs,
        )
        self._n = n

    @override
    def enter(self: Draw, context: IExecutionContext) -> None:
        """Move n cards from a player's deck to their hand."""
        super().enter(context=context)

        for _ in range(self._n):
            card: ICard = context.player.main_cards.pop()
            context.player.hand.append(card)
