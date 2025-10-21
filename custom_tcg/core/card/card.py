"""A generic card implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from custom_tcg.core.interface import (
    IAction,
    ICard,
    IEffect,
    IExecutionContext,
    INamed,
    IPlayer,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.dimension import CardClass, CardType


class Card(ICard, INamed):
    """A generic card implementation."""

    player: IPlayer
    types: list[CardType]
    classes: list[CardClass]
    actions: list[IAction]
    effects: list[IEffect]
    action_registry: list[IAction]

    def __init__(  # noqa: PLR0913
        self: Card,
        name: str,
        player: IPlayer,
        types: list[CardType],
        classes: list[CardClass],
        actions: list[IAction] | None = None,
        effects: list[IEffect] | None = None,
    ) -> None:
        """Create a tcg card."""
        self.session_object_id = uuid4().hex
        self.name = name
        self.player = player
        self.types = types
        self.classes = classes
        self.actions = actions or []
        self.effects = effects or []
        self.action_registry = []

    @classmethod
    def create(cls: type[Card], player: IPlayer) -> ICard:
        """Create an instance of this card."""
        raise NotImplementedError

    def register(self: Card, action: IAction) -> Card:
        """Allow actions to be tracked for binding."""
        self.action_registry.append(action)
        return self

    def map_binding_operation(
        self: Card,
        context: IExecutionContext,
        operation: Callable[[IAction, IAction], None],
    ) -> None:
        """Apply a operation to all potential bindings with this card."""
        for existing, entering in (
            (existing_action, entering_action)
            for player in context.players
            for card in player.played
            for existing_action in card.action_registry
            for entering_action in self.action_registry
            if existing_action.card is not self
        ):
            operation(existing, entering)

    def add_binding(self: Card, existing: IAction, entering: IAction) -> None:
        """Apply a single binding."""
        if existing.bind is not None and existing.bind(
            entering,
            entering.card,
            entering.player,
        ):
            entering.notify.append(existing)

        if entering.bind is not None and entering.bind(
            existing,
            existing.card,
            existing.player,
        ):
            existing.notify.append(entering)

    def add_bindings(self: Card, context: IExecutionContext) -> None:
        """Subscribe all known actions to each other."""
        self.map_binding_operation(
            context=context,
            operation=self.add_binding,
        )

    def remove_binding(
        self: Card,
        existing: IAction,
        exiting: IAction,
    ) -> None:
        """Remove a single binding."""
        if existing.bind is not None and existing.bind(
            exiting,
            exiting.card,
            exiting.player,
        ):
            exiting.notify.remove(existing)

        if exiting.bind is not None and exiting.bind(
            existing,
            existing.card,
            existing.player,
        ):
            existing.notify.remove(exiting)

    def remove_bindings(self: Card, context: IExecutionContext) -> None:
        """Unsubscribe all known actions from each other."""
        self.map_binding_operation(
            context=context,
            operation=self.remove_binding,
        )
