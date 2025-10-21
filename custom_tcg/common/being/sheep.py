"""Create Sheep instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Sheep(Card):
    """Create Sheep instances."""

    name: str = "Sheep"

    @classmethod
    def create(cls: type[Sheep], player: IPlayer) -> Sheep:
        """Create a Sheep instance."""
        sheep = Sheep(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.animal, CardClassDef.fluffy_animal],
        )

        sheep.actions.append(
            Play(card=sheep, player=player),
        )

        sheep.effects.append(
            BeingStats(
                name="Base stats",
                card=sheep,
                strength=0,
                dexterity=0,
                constitution=3,
                intelligence=0,
                wisdom=0,
                charisma=0,
            ),
        )

        return sheep
