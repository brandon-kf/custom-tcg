"""Create Peasant instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.draw import Draw
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Peasant(Card):
    """Create Peasant instances."""

    name: str = "Peasant"

    @classmethod
    def create(cls: type[Peasant], player: IPlayer) -> Peasant:
        """Create a Peasant instance."""
        peasant = Peasant(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        peasant.actions.append(
            Play(card=peasant, player=player),
        )

        peasant.actions.append(
            Activate(
                actions=[
                    Draw(
                        n=1,
                        card=peasant,
                        player=player,
                    ),
                ],
                card=peasant,
                player=player,
            ),
        )

        peasant.effects.append(
            BeingStats(
                name="Base stats",
                card=peasant,
                strength=1,
                dexterity=1,
                constitution=1,
                intelligence=1,
                wisdom=1,
                charisma=1,
            ),
        )

        return peasant
