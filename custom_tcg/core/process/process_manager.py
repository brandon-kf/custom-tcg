"""An action activated by a process to manage itself."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.process.end_process import EndProcess
from custom_tcg.core.process.reset_actions import ResetActions

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class ProcessManager(Action):
    """An action activated by a process to manage itself."""

    end_process: EndProcess
    reset_actions: ResetActions

    def __init__(
        self: ProcessManager,
        name: str,
        card: ICard,
        player: IPlayer,
        reset_actions: Callable[[IAction], bool] | None = None,
    ) -> None:
        """Create a process manager."""
        super().__init__(
            name=name,
            card=card,
            player=player,
        )
        self.end_process = EndProcess(card=card, player=player)
        self.reset_actions = ResetActions(
            card=card,
            player=player,
            filter_actions=lambda action: (
                (reset_actions or (lambda action: False))(action)  # noqa: ARG005
                and action.card is not card
                and action.player is player
            ),
        )
        card.actions.extend((self.end_process, self.reset_actions))

    @override
    def enter(
        self: ProcessManager,
        context: IExecutionContext,
    ) -> None:
        """On enter, populate choices for the first time."""
        super().enter(context=context)

        self.end_process.state = ActionStateDef.not_started
        self.update_next_state(context=context)

    @override
    def request_input(
        self: ProcessManager,
        context: IExecutionContext,
    ) -> None:
        super().request_input(context=context)

        self.update_choices(context=context)

    @override
    def receive_input(
        self: ProcessManager,
        context: IExecutionContext,
    ) -> None:
        super().receive_input(context=context)

        self.update_next_state(context=context)

    @override
    def complete(
        self: ProcessManager,
        context: IExecutionContext,
    ) -> None:
        super().complete(context=context)

        context.choices = []
        context.execute(action=self.reset_actions)

    @override
    def cancel(
        self: ProcessManager,
        context: IExecutionContext,
    ) -> None:
        # Ignore any cancellations.
        self.update_next_state(context=context)

    def update_next_state(
        self: ProcessManager,
        context: IExecutionContext,
    ) -> None:
        """Regardless of current state, decide where to go."""
        self.update_choices(context=context)

        if len(context.notifications) > 0:
            for action in context.notifications:
                action.state = ActionStateDef.queued
            context.ready = [*context.notifications, *context.ready]
            context.notifications = []
            self.state = ActionStateDef.queued

        elif (
            len(context.notifications) == 0
            and self.end_process.state == ActionStateDef.not_started
        ):
            self.state = ActionStateDef.input_requested

        else:
            self.state = ActionStateDef.completed

    def update_choices(
        self: ProcessManager,
        context: IExecutionContext,
    ) -> None:
        """Create play and activation actions, add to context."""
        context.choices = [self.end_process]
