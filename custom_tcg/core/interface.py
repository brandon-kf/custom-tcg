"""Provide key interfaces for structural abstraction, to be subclassed."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.dimension import (
        ActionState,
        CardClass,
        CardType,
        EffectState,
    )


logger: logging.Logger = logging.getLogger(name=__name__)


class INamed:
    """Allow many types of objects to be identifiable by name."""

    name: str


class ISessionTracked:
    """Allow many types of objects to be identifiable within a session."""

    session_object_id: str


class IPlayer(INamed, ISessionTracked):
    """A tcg match player."""

    decks: list[IDeck]
    starting_cards: list[ICard]
    main_cards: list[ICard]
    processes: list[ICard]
    hand: list[ICard]
    played: list[ICard]
    discard: list[ICard]

    def select_deck(self: IPlayer, deck: IDeck) -> None:
        """Select a deck for play."""
        self.starting_cards = deck.starting
        self.main_cards = deck.main


class IDeck(INamed):
    """A deck of cards."""

    player: IPlayer
    starting: list[ICard]
    main: list[ICard]


class ICard(INamed, ISessionTracked):
    """A tcg card."""

    player: IPlayer
    types: list[CardType]
    classes: list[CardClass]
    actions: list[IAction]
    effects: list[IEffect]
    action_registry: list[IAction]

    @classmethod
    def create(cls: type[ICard], player: IPlayer) -> ICard:
        """Create an instance of this card."""
        raise NotImplementedError

    def register(self: ICard, action: IAction) -> ICard:
        """Allow actions to be tracked for binding."""
        raise NotImplementedError

    def map_binding_operation(
        self: ICard,
        context: IExecutionContext,
        operation: Callable[[IAction, IAction], None],
    ) -> None:
        """Apply a operation to all potential bindings with this card."""
        raise NotImplementedError

    def add_binding(self: ICard, existing: IAction, entering: IAction) -> None:
        """Subscribe one action to another."""
        raise NotImplementedError

    def add_bindings(self: ICard, context: IExecutionContext) -> None:
        """Subscribe all known actions to each other."""
        raise NotImplementedError

    def remove_binding(
        self: ICard,
        existing: IAction,
        exiting: IAction,
    ) -> None:
        """Unsubscribe one action from another."""
        raise NotImplementedError

    def remove_bindings(self: ICard, context: IExecutionContext) -> None:
        """Unsubscribe all known actions from each other."""
        raise NotImplementedError


class IAction(INamed, ISessionTracked):
    """An action to be executed in a match."""

    card: ICard
    player: IPlayer
    state: ActionState
    selectors: list[IAction]
    costs: list[IAction]
    bind: Callable[[IAction, ICard, IPlayer], bool] | None
    notify: list[IAction]

    def reset_state(self: IAction) -> None:
        """Reset any stored information that is stateful."""
        raise NotImplementedError

    def queue(self: IAction, context: IExecutionContext) -> None:
        """Respond to state `ActionStateDef.queued`."""
        raise NotImplementedError

    def enter(self: IAction, context: IExecutionContext) -> None:
        """Respond state `ActionStateDef.entered`."""
        raise NotImplementedError

    def request_input(self: IAction, context: IExecutionContext) -> None:
        """Respond state `ActionStateDef.input_requested`."""
        raise NotImplementedError

    def receive_input(self: IAction, context: IExecutionContext) -> None:
        """Respond state `ActionStateDef.input_received`."""
        raise NotImplementedError

    def complete(self: IAction, context: IExecutionContext) -> None:
        """Respond state `ActionStateDef.succeeded`."""
        raise NotImplementedError

    def cancel(self: IAction, context: IExecutionContext) -> None:
        """Respond state `ActionStateDef.cancelled`."""
        raise NotImplementedError


class IEffect(INamed, ISessionTracked):
    """An effect applied to a card."""

    card: ICard
    player: IPlayer
    state: EffectState
    actions: list[IAction]
    bind_removal: Callable[[IAction, ICard, IPlayer], bool]

    @classmethod
    def create(cls: type[IEffect], card: ICard) -> IEffect:
        """Create an instance of this effect."""
        raise NotImplementedError

    def copy(self: IEffect, card: ICard) -> IEffect:
        """Create an instance of this effect."""
        raise NotImplementedError

    def activate(self: IEffect, context: IExecutionContext) -> None:
        """Make this effect active."""
        raise NotImplementedError

    def deactivate(self: IEffect, context: IExecutionContext) -> None:
        """Make this effect inactive."""
        raise NotImplementedError

    def bind_deactivation(self: IEffect, context: IExecutionContext) -> bool:
        """Specify when this effect should deactivate."""
        raise NotImplementedError


class IActionContext:
    """A class to store info about an event that occurred."""

    action: IAction
    ready: list[IAction]
    choices: list[IAction]
    players: list[IPlayer]


class IActionQueue(Protocol):
    """A queue of events that has occurred."""

    def append(self: IActionQueue, action_context: IActionContext, /) -> None:
        """Add a new event to the queue."""
        raise NotImplementedError


class IExecutionContext:
    """Match context for an action."""

    player: IPlayer
    process: ICard
    ready: list[IAction]
    choices: list[IAction]
    notifications: list[IAction]
    completed: IActionQueue | None
    players: list[IPlayer]

    def execute(self: IExecutionContext, action: IAction) -> None:
        """Execute an action."""
        raise NotImplementedError

    def post_execute(self: IExecutionContext, action: IAction) -> None:
        """Update changes to effects, notifications, etc."""
        raise NotImplementedError

    def dequeue(self: IExecutionContext, action: IAction) -> None:
        """Remove an action from any queues."""
        raise NotImplementedError

    def push(self: IExecutionContext, action: IAction) -> None:
        """Push execution state to stack and start a new one."""
        raise NotImplementedError

    def pop(self: IExecutionContext) -> None:
        """Pop prior execution state and combine with current."""
        raise NotImplementedError
