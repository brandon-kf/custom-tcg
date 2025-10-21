"""Create Pile of Rocks instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class PileOfRocks(Card):
    """Create Pile of Rocks instances."""

    name: str = "Pile of Rocks"

    @classmethod
    def create(cls: type[PileOfRocks], player: IPlayer) -> PileOfRocks:
        """Create a Pile of Rocks instance."""
        pile_of_rocks = PileOfRocks(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.bulk_material],
        )

        pile_of_rocks.actions.append(
            Play(card=pile_of_rocks, player=player),
        )

        pile_of_rocks.effects.append(
            ItemStats(
                name="Base stats",
                card=pile_of_rocks,
                heft=2,
                antiquity=1,
            ),
        )

        return pile_of_rocks
