"""Create Let's Rest instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import CardClassDef, CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play
from custom_tcg.core.process.process_manager import ProcessManager
from custom_tcg.core.process.rest import Rest

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class LetsRest(Card):
    """Create Let's Play instances."""

    name: str = "Let's Rest"

    @classmethod
    def create(cls: type[LetsRest], player: IPlayer) -> LetsRest:
        """Create a Let's Rest instance."""
        lets_rest = LetsRest(
            name=cls.name,
            player=player,
            types=[CardTypeDef.process],
            classes=[CardClassDef.rest],
        )

        lets_rest.actions.append(
            Play(card=lets_rest, player=player),
        )

        lets_rest.actions.append(
            Activate(
                actions=[
                    Rest(card=lets_rest, player=player),
                    ProcessManager(
                        name=f"End the '{LetsRest.name}' process",
                        card=lets_rest,
                        player=player,
                    ),
                ],
                card=lets_rest,
                player=player,
            ),
        )

        return lets_rest
