"""Core player implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, override

from custom_tcg.core.action import Action as NonAnonAction
from custom_tcg.core.interface import (
    IAction,
    ICard,
    IDeck,
    IExecutionContext,
    IPlayer,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.dimension import ActionState


class Action(NonAnonAction):
    """A generic action implementation."""

    _enter: Callable[[IExecutionContext], Any]

    def __init__(  # noqa: PLR0913
        self: Action,
        name: str,
        card: ICard,
        player: IPlayer,
        enter: Callable[[IExecutionContext], Any],
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
        state: ActionState | None = None,
    ) -> None:
        """Create an action."""
        super().__init__(
            name=name,
            card=card,
            player=player,
            bind=bind,
            costs=costs,
            state=state,
        )
        self._enter = enter

    @override
    def enter(self: Action, context: IExecutionContext) -> Any:
        super().enter(context=context)

        self._enter(context)


@dataclass
class Player(IPlayer):
    """A tcg match player."""

    session_object_id: str
    name: str
    decks: list[IDeck]
    starting_cards: list[ICard]
    main_cards: list[ICard]
    processes: list[ICard]
    hand: list[ICard]
    played: list[ICard]
    discard: list[ICard]


@dataclass
class Deck(IDeck):
    """A deck of cards."""

    name: str
    player: IPlayer
    starting: list[ICard]
    main: list[ICard]
