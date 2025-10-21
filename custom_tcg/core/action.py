"""A generalized implementation of an action."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override
from uuid import uuid4

from custom_tcg.core.dimension import ActionState, ActionStateDef
from custom_tcg.core.interface import IAction, ICard, IExecutionContext, IPlayer

if TYPE_CHECKING:
    from collections.abc import Callable

logger: logging.Logger = logging.getLogger(name=__name__)


class Action(IAction):
    """An action to be executed in a match."""

    def __init__(  # noqa: PLR0913
        self: Action,
        card: ICard,
        player: IPlayer,
        state: ActionState | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
        name: str | None = None,
    ) -> None:
        """Create an action."""
        self.session_object_id = uuid4().hex
        self.name = name or "Action"
        self.card = card.register(action=self)
        self.player = player
        self.state = state or ActionStateDef.not_started
        self.bind = bind
        self.notify = []
        self.selectors = []
        self.costs = costs or []

        if self.state not in (
            ActionStateDef.not_started,
            ActionStateDef.stateless,
        ):
            raise NotImplementedError

    def change_state(self: Action, state: ActionState) -> None:
        """Log and perform a state change."""
        logger.info(
            "Action '%s' changed state (%s -> %s)",
            self.name,
            self.state.name,
            state.name,
        )
        self.state = state

    @override
    def reset_state(self: Action) -> None:
        """Reset any stored information that is stateful."""
        self.change_state(state=ActionStateDef.not_started)

    @override
    def queue(self: Action, context: IExecutionContext) -> None:
        """Change state to `ActionStateDef.queued`."""
        self.change_state(state=ActionStateDef.queued)

    @override
    def enter(self: Action, context: IExecutionContext) -> None:
        """Change state to `ActionStateDef.entered`."""
        self.change_state(state=ActionStateDef.entered)

    @override
    def request_input(self: Action, context: IExecutionContext) -> None:
        """Change state to `ActionStateDef.request_input`."""
        self.change_state(state=ActionStateDef.input_requested)

    @override
    def receive_input(self: Action, context: IExecutionContext) -> None:
        """Change state to `ActionStateDef.input_received`."""
        self.change_state(state=ActionStateDef.input_received)

    @override
    def complete(self: Action, context: IExecutionContext) -> None:
        """Change state to `ActionStateDef.succeeded`."""
        self.change_state(state=ActionStateDef.completed)

    @override
    def cancel(self: Action, context: IExecutionContext) -> None:
        """Change state to `ActionStateDef.cancelled`."""
        self.change_state(state=ActionStateDef.cancelled)
