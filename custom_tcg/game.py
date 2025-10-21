"""Play a game!."""

from __future__ import annotations

import logging
from secrets import randbelow
from typing import TYPE_CHECKING
from uuid import uuid4

from custom_tcg.core import util
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.execution import ExecutionContext
from custom_tcg.core.execution.play import Play
from custom_tcg.core.execution.resolve import Resolve
from custom_tcg.core.interface import IAction, IPlayer

if TYPE_CHECKING:
    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )

logger: logging.Logger = logging.getLogger(name=__name__)


class Game:
    """Play a game!."""

    session_id: str
    players: list[IPlayer]
    context: IExecutionContext
    prev_action: IAction
    prev_count: int = 0

    def __init__(self: Game, players: list[IPlayer]) -> None:
        """Create a game."""
        self.session_id = uuid4().hex
        self.players = []
        self.context = ExecutionContext(players=players)
        self.prev_action = self.context.player.main_cards[0].actions[0]

        for player in players:
            self.add_player(player=player)

    def add_player(self: Game, player: IPlayer) -> None:
        self.players.append(player)

        for card_, action_ in (
            (card, action)
            for card in player.starting_cards
            for action in card.actions
            if isinstance(action, Play)
        ):
            player.hand.append(card_)
            self.context.ready.append(action_)
            action_.state = ActionStateDef.queued

    def setup(self: Game) -> None:
        for player in self.players:
            player.main_cards = util.list_randomize(ordered=player.main_cards)
        random_first_index: int = randbelow(
            exclusive_upper_bound=len(self.players),
        )
        self.players = (
            self.players[random_first_index:]
            + self.players[:random_first_index]
        )
        self.context.players = self.players
        self.context.ready.sort(
            key=lambda action: self.players.index(action.player),
        )

    def start(self: Game) -> list[IAction]:
        """Play starting hands with no resolution from bindings.

        Then queue up the first process for the first player.
        """
        while len(self.context.ready) > 0:
            action: IAction = self.context.ready[0]
            logger.info(
                "Starting action '%s' for player '%s' executing.",
                action.name,
                action.player.name,
            )
            self.context.player = action.player
            self.context.execute(action=action)

        self.context.notifications = []

        self.context.player = self.players[0]
        first_process: ICard = self.context.player.processes[0]

        self.context.ready = [
            Resolve(
                action=next(
                    action
                    for action in first_process.actions
                    if isinstance(action, Activate)
                ),
                card=first_process,
                player=self.context.player,
            ),
        ]
        self.context.ready[0].state = ActionStateDef.queued
        self.context.notifications = []

        self.execute_ready_queue()
        return self.context.choices

    def choose(self: Game, action: IAction) -> list[IAction]:
        """Execute a chosen action and evaluate any ready actions."""
        choice_for_action: bool = len(self.context.ready) > 0

        self.context.execute(action=action)

        if choice_for_action:
            self.context.ready[0].state = ActionStateDef.input_received
            self.context.execute(action=self.context.ready[0])

        logger.info(msg=self.context)

        self.execute_ready_queue()
        return self.context.choices

    def execute_ready_queue(self: Game) -> None:
        """Continuously execute the ready action until a choice is needed."""
        while (
            len(self.context.ready) > 0
            and self.context.ready[0].state != ActionStateDef.input_requested
        ):
            self.prev_action = self.context.ready[0]

            self.context.execute(action=self.context.ready[0])
            logger.info(msg=self.context)

            if (
                len(self.context.ready) == 0
                or self.context.ready[0] != self.prev_action
            ):
                self.prev_count = 0
            else:
                self.prev_count += 1

            if self.prev_count > 10:  # noqa: PLR2004
                raise Exception("Max duplicate ready action occurred.")  # noqa: TRY003, TRY002, EM101


if __name__ == "__main__":
    from src.main import setup
    from custom_tcg.common.player import p1, p2
    from custom_tcg.game import Game

    setup()

    game: Game = Game(players=[p1(), p2()])
    game.start()
