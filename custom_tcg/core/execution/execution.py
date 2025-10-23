"""Core functionality for a custom tcg."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.execution.resolve import Resolve
from custom_tcg.core.interface import (
    IAction,
    IActionContext,
    IActionQueue,
    ICard,
    IExecutionContext,
    IPlayer,
)
from custom_tcg.core.process.reset_actions import ResetActions

if TYPE_CHECKING:
    from collections.abc import Generator

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class ActionContext(IActionContext):
    """Implementation for executed states."""

    action: IAction
    ready: list[IAction]
    choices: list[IAction]
    players: list[IPlayer]


class ExecutionContext(IExecutionContext):
    """Match context for an action."""

    player: IPlayer
    process: ICard
    ready: list[IAction]
    choices: list[IAction]
    notifications: list[IAction]
    completed: IActionQueue | None
    players: list[IPlayer]

    def __init__(
        self: ExecutionContext,
        players: list[IPlayer],
        completed: IActionQueue | None = None,
    ) -> None:
        """Create an execution context."""
        self.player = players[0]
        self.process = Card(
            name="Placeholder",
            player=self.player,
            types=[],
            classes=[],
        )
        self.ready = []
        self.choices = []
        self.notifications = []
        self.completed = completed
        self.players = players

    def execute(self: ExecutionContext, action: IAction) -> None:
        """Execute an action."""
        logger.info(
            "Attempt to execute '%s' from card '%s'",
            action.name,
            action.card.name,
        )

        next_action: IAction = action

        # Consider dependent selector and cost actions, then queue and provide
        # the next action for execution (which will be the passed action if
        # no outstanding dependents remain.)
        self.speculate(action=next_action)

        if next_action.state != ActionStateDef.cancelled:
            next_action: IAction = self.next_dependent(action=next_action)

        # Poke the action to prepare for receiving input.
        if next_action.state == ActionStateDef.input_received:
            next_action.receive_input(context=self)

        # Enter (execute) this action if necessary.
        if next_action.state in (ActionStateDef.queued, ActionStateDef.entered):
            next_action.enter(context=self)

        # If the action was executed the first time and showed no state
        # interaction whatsoever, it is assumed to have completed successfully
        # with no interest in tracking future state.
        if next_action.state == ActionStateDef.entered:
            next_action.state = ActionStateDef.completed

        if next_action.state == ActionStateDef.completed:
            next_action.complete(context=self)

        if next_action.state == ActionStateDef.cancelled:
            next_action.cancel(context=self)

        # Post-execute on success.
        if next_action.state == ActionStateDef.completed:
            logger.info("  Post-executing '%s'", next_action.name)
            self.post_execute(action=next_action)

        if (
            next_action.state
            in (
                ActionStateDef.completed,
                ActionStateDef.cancelled,
            )
            and self.completed is not None
        ):
            logger.info("  Queueing event for a completed action")
            self.completed.append(
                ActionContext(
                    action=next_action,
                    ready=list(self.ready),
                    choices=list(self.choices),
                    players=list(self.players),
                ),
            )

        # Dequeue if done executing. Pop state if necessary.
        if next_action.state in (
            ActionStateDef.completed,
            ActionStateDef.cancelled,
        ):
            logger.info("  Dequeueing '%s'", next_action.name)
            self.dequeue(action=next_action)

        if (
            len(self.ready) > 0
            and self.ready[0].state == ActionStateDef.input_requested
        ):
            self.ready[0].request_input(context=self)

    def speculate(
        self: ExecutionContext,
        action: IAction,
    ) -> None:
        """Check all dependent actions and execute `queue` speculatively."""
        next_action: IAction | None = action
        stack: list[IAction] = []
        cancellation_found: bool = False

        while next_action is not None:
            dependents: Generator[IAction, None, None] = (
                stateful
                for stateful in (*next_action.selectors, *next_action.costs)
                if stateful.state != ActionStateDef.completed
            )

            stack.extend(dependents)

            if next_action.state == ActionStateDef.not_started:
                logger.info(
                    "  Check cancellation of dependent '%s'",
                    next_action.name,
                )

                next_action.queue(context=self)

                if next_action.state == ActionStateDef.cancelled:
                    logger.info(
                        "  Found cancellation of dependent '%s'",
                        next_action.name,
                    )
                    cancellation_found = True
                    stack.clear()

                next_action.reset_state()

            next_action = stack.pop() if len(stack) > 0 else None

        if cancellation_found:
            action.state = ActionStateDef.cancelled
            logger.info(
                "  Cancelled action '%s' due to dependent cancellation",
                action.name,
            )

    def next_dependent(self: ExecutionContext, action: IAction) -> IAction:
        """Find the first dependent actions that still needs execution."""
        # Push state on the parent action, even if it won't execute yet.
        next_action: IAction | None = action

        while next_action is not None:
            if next_action.state == ActionStateDef.not_started:
                logger.info("  Queueing '%s'", next_action.name)
                self.ready = [next_action, *self.ready]
                next_action.queue(context=self)

            # Selector and cost results are used by the action. They are always
            # stateful. They must be satisfied or cancelled before the desired
            # action is executed.
            dependents: Generator[IAction, None, None] = (
                stateful
                for stateful in (*next_action.selectors, *next_action.costs)
                if stateful.state != ActionStateDef.completed
            )
            next_dependent: IAction | None = next(iter(dependents), None)

            # If any dependent was cancelled, pass execution back to the parent
            # and cancel it too.
            if (
                next_dependent is not None
                and next_dependent.state == ActionStateDef.cancelled
            ):
                next_action.state = ActionStateDef.cancelled
                next_dependent = None

            next_action = next_dependent

        return self.ready[0]

    def post_execute(self: ExecutionContext, action: IAction) -> None:
        """Update changes to effects, notifications, etc."""
        # TODO: Effect removal on bind.  # noqa: TD002, FIX002, TD003
        # for effect, affected_card in (
        #     (effect, card)
        #     for player in self.players
        #     for card in player.played
        #     for effect in card.effects
        # ):
        #     if effect.bind_removal(
        #         action,
        #         action.card,
        #         action.card.player,
        #     ):
        #         self.ready.append(
        #             Resolve(
        #                 action=RemoveEffect(
        #                     effect_to_remove=effect,
        #                     card_to_remove_from=affected_card,
        #                     card=action.card,
        #                     player=action.player,
        #                 ),
        #                 card=action.card,
        #                 player=action.player,
        #             ),
        #         )

        self.notifications.extend(
            Resolve(
                action=notification,
                card=notification.card,
                player=notification.player,
            )
            for notification in action.notify
            if notification.card in action.player.played
        )

    def dequeue(self: ExecutionContext, action: IAction) -> None:
        """Remove an action from ready or choice queues."""
        if action in self.ready:
            logger.info(
                "Action '%s' found in ready after execution, dequeueing.",
                action.name,
            )
            self.ready.remove(action)

        if action in self.choices:
            logger.info(
                "Action '%s' found in choice after execution, dequeueing.",
                action.name,
            )
            self.choices.remove(action)

        if action.bind is not None:
            this_action: IAction = action

            self.notifications.append(
                ResetActions(
                    card=action.card,
                    player=action.player,
                    filter_actions=lambda action: action is this_action,
                ),
            )

    def __repr__(self: ExecutionContext) -> str:
        """Create a string representation of a context."""
        return (
            "ActionContext(\n"
            f"  player=Player(\n"
            f"    name={self.player.name},\n"
            f"    starting_cards={[card.name for card in self.player.starting_cards]},\n"  # noqa: E501
            f"    main_cards={[card.name for card in self.player.main_cards]},\n"  # noqa: E501
            f"    hand={[card.name for card in self.player.hand]},\n"
            f"    processes={[card.name for card in self.player.processes]},\n"
            f"    play={[card.name for card in self.player.played]},\n"
            f"    discard={[card.name for card in self.player.discard]},\n"
            "  ),\n"
            f"  process={self.process.name},\n"
            f"  ready={[action.name for action in self.ready]},\n"
            f"  choices={[action.name for action in self.choices]},\n"
            f"  notifications={[action.name for action in self.notifications]},\n"  # noqa: E501
            f"  players={[player.name for player in self.players]})\n"
            "),"
        )
