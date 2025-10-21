"""Create Let's Play instances."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import CardClassDef, CardTypeDef
from custom_tcg.core.effect.effect import Activated
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play
from custom_tcg.core.interface import IPlayer
from custom_tcg.core.process.process_manager import ProcessManager

if TYPE_CHECKING:
    from custom_tcg.core.interface import (
        ICard,
        IExecutionContext,
        IPlayer,
    )


class LetsPlay(Card):
    """Create Let's Play instances."""

    name: str = "Let's Play"

    @classmethod
    def create(cls: type[LetsPlay], player: IPlayer) -> LetsPlay:
        """Create a Let's Play instance."""
        lets_play = LetsPlay(
            name=cls.name,
            player=player,
            types=[CardTypeDef.process],
            classes=[CardClassDef.play],
        )

        lets_play.actions.append(
            Play(card=lets_play, player=player),
        )

        lets_play.actions.append(
            Activate(
                actions=[
                    LetsPlay.ProcessManager(
                        card=lets_play,
                        player=player,
                    ),
                ],
                card=lets_play,
                player=player,
            ),
        )

        return lets_play

    class ProcessManager(ProcessManager):
        """Create optional choices for players to select."""

        def __init__(
            self: LetsPlay.ProcessManager,
            card: ICard,
            player: IPlayer,
        ) -> None:
            """Create a choice manager."""
            super().__init__(
                name=(
                    "Choose any number of cards to play or activate, "
                    f"or end the '{LetsPlay.name}' process"
                ),
                card=card,
                player=player,
                reset_actions=lambda action: (
                    isinstance(
                        action,
                        (Play, Activate),
                    )
                ),
            )

        @override
        def update_choices(
            self: LetsPlay.ProcessManager,
            context: IExecutionContext,
        ) -> None:
            """Create play and activation actions, add to context."""
            super().update_choices(context=context)

            context.choices = [
                *(
                    action
                    for card in context.player.hand
                    for action in card.actions
                    if isinstance(action, Play) and action.bind is None
                ),
                *(
                    action
                    for card in context.player.played
                    for action in card.actions
                    if isinstance(action, Activate)
                    and action.bind is None
                    and not any(
                        isinstance(effect, Activated) for effect in card.effects
                    )
                    and CardTypeDef.being in card.types
                ),
                self.end_process,
            ]
