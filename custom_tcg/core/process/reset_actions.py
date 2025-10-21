"""Reset a filtered set of actions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.dimension import ActionState
    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


logger: logging.Logger = logging.getLogger(name=__name__)


class ResetActions(Action):
    """Reset a filtered set of actions."""

    filter_actions: Callable[[IAction], bool]

    def __init__(  # noqa: PLR0913
        self: ResetActions,
        card: ICard,
        player: IPlayer,
        filter_actions: Callable[[IAction], bool],
        state: ActionState | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
    ) -> None:
        """Create a reset actions action."""
        super().__init__(
            name="Reset actions",
            card=card,
            player=player,
            state=state,
            bind=bind,
            costs=costs,
        )
        self.filter_actions = filter_actions

    @override
    def enter(self: ResetActions, context: IExecutionContext) -> None:
        super().enter(context=context)

        filtered: list[IAction] = [
            action
            for player in context.players
            for card in player.played
            for action in card.actions
            if self.filter_actions(action)
            # If we try to reset this action, it'll go infinite in execution.
            and action is not self
        ]

        logger.info("Resetting actions:")
        logger.info([action.name for action in filtered])

        for action in filtered:
            action.reset_state()
