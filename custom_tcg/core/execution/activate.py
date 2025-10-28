"""Activate a card for effect."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action
from custom_tcg.core.card.tap import Tap
from custom_tcg.core.dimension import ActionStateDef, CardTypeDef
from custom_tcg.core.execution.resolve import Resolve
from custom_tcg.core.interface import IAction

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class Activate(Action):
    """Activate a card for effect."""

    actions: list[IAction]

    def __init__(
        self: Activate,
        card: ICard,
        player: IPlayer,
        actions: list[IAction],
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
    ) -> None:
        """Create an activation."""
        super().__init__(
            name=(
                f"Activate from card '{card.name}'"
                f" action(s): '{', '.join([a.name for a in actions])}'"
            ),
            card=card,
            player=player,
            bind=bind,
            costs=costs,
        )
        self.actions = list(actions)

    @override
    def reset_state(self: Activate) -> None:
        super().reset_state()

        for action in self.actions:
            action.reset_state()

    @override
    def enter(self: Activate, context: IExecutionContext) -> None:
        super().enter(context=context)

        append_queue: list[IAction] = context.notifications

        if CardTypeDef.process in self.card.types:
            context.process = self.card
            append_queue = context.ready

        activated_actions: list[IAction] = [
            Tap(
                cards_to_activate=[self.card],
                card=self.card,
                player=self.player,
            ),
            *(
                Resolve(
                    action=action,
                    card=self.card,
                    player=self.player,
                )
                for action in self.actions
            ),
        ]

        for action in activated_actions:
            action.state = ActionStateDef.queued

        append_queue.extend(activated_actions)
