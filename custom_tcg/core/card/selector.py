"""A generic selector composed into actions."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action
from custom_tcg.core.anon import Action as AnonymousAction
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.interface import IExecutionContext

if TYPE_CHECKING:
    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        INamed,
        IPlayer,
    )


logger: logging.Logger = logging.getLogger(name=__name__)


class Selector(Action):
    """A generic selector composed into actions."""

    options: list[INamed]
    selected: list[INamed]
    accept_n: Callable[[int], bool]
    require_n: bool
    create_options: Callable[[IExecutionContext], list]
    confirm_action: IAction
    cancel_action: IAction

    def __init__(  # noqa: PLR0913
        self: Selector,
        accept_n: Callable[[int], bool],
        require_n: bool,  # noqa: FBT001
        options: list | Callable[[IExecutionContext], list],
        name: str,
        card: ICard,
        player: IPlayer,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Construct a selector."""
        super().__init__(
            name=name,
            card=card,
            player=player,
            bind=bind,
        )

        self.accept_n = accept_n
        self.require_n = require_n

        # Simplify convenient options parameter to be reproduced each state.
        self.create_options = (
            options
            if isinstance(options, Callable)
            else (lambda context: list(options))  # noqa: ARG005
        )

        self.confirm_action = AnonymousAction(
            name="Confirm",
            card=self.card,
            player=self.player,
            enter=lambda context: None,  # noqa: ARG005
        )

        self.cancel_action = AnonymousAction(
            name="Cancel",
            card=self.card,
            player=self.player,
            enter=lambda context: None,  # noqa: ARG005
        )

        self._init_state()

    def _init_state(self: Selector) -> None:
        self.reset_state()

    @override
    def reset_state(self: Selector) -> None:
        """Get this selector ready for its next use."""
        super().reset_state()
        self.options = []
        self.selected = []
        self.confirm_action.state = ActionStateDef.not_started
        self.cancel_action.state = ActionStateDef.not_started

    @override
    def queue(self: Selector, context: IExecutionContext) -> None:
        super().queue(context=context)

        options: list = self.create_options(context)
        option_count: int = len(options)

        if not any(self.accept_n(n) for n in range(option_count + 1)):
            logger.info(options)
            self.state = ActionStateDef.cancelled

    @override
    def enter(self: Selector, context: IExecutionContext) -> None:
        """Create selector choices."""
        super().enter(context=context)

        self.options = self.create_options(context)

        context.choices = [
            *(
                SelectorChoice(
                    name=f"Select '{option.name}'",
                    selected=option,
                    selector=self,
                    card=self.card,
                    player=self.player,
                )
                for option in self.options
            ),
        ]

        context.choices.append(self.confirm_action)

        if not self.require_n:
            context.choices.append(self.cancel_action)

        self.state = ActionStateDef.input_requested

    @override
    def receive_input(self: Selector, context: IExecutionContext) -> None:
        """Evaluate if the selector acceptance criteria was satisfied."""
        super().receive_input(context=context)

        if (
            self.confirm_action.state == ActionStateDef.completed
            and self.accept_n(
                len(self.selected),
            )
        ):
            self.state = ActionStateDef.completed

        elif self.confirm_action.state == ActionStateDef.completed:
            self.confirm_action.state = ActionStateDef.not_started
            context.choices.append(self.confirm_action)

            # If cancel action is present, swap it to the end.
            if not self.require_n:
                context.choices[-2], context.choices[-1] = (
                    context.choices[-1],
                    context.choices[-2],
                )

            self.state = ActionStateDef.input_requested

        elif self.cancel_action.state == ActionStateDef.completed:
            self.state = ActionStateDef.cancelled

        else:
            self.state = ActionStateDef.input_requested

    @override
    def complete(self: Selector, context: IExecutionContext) -> None:
        """Make sure choices don't spill over anywhere else."""
        super().complete(context=context)

        context.choices = []

    @override
    def cancel(self: Selector, context: IExecutionContext) -> None:
        """Make sure choices don't spill over anywhere else."""
        super().cancel(context=context)

        context.choices = []


class SelectorChoice(Action):
    """A single choice to select, generated by a `Selector`."""

    selector: Selector
    selected: INamed

    def __init__(  # noqa: PLR0913
        self: SelectorChoice,
        name: str,
        selected: INamed,
        selector: Selector,
        card: ICard,
        player: IPlayer,
    ) -> None:
        """Create a selector choice."""
        super().__init__(
            name=name,
            card=card,
            player=player,
        )
        self.selector = selector
        self.selected = selected

    @override
    def enter(self: SelectorChoice, context: IExecutionContext) -> None:
        super().enter(context=context)

        self.selector.selected.append(self.selected)
