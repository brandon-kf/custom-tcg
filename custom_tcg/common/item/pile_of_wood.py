"""Create Pile of Wood instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class PileOfWood(Card):
    """Create Pile of Wood instances."""

    name: str = "Pile of Wood"

    @classmethod
    def create(cls: type[PileOfWood], player: IPlayer) -> PileOfWood:
        """Create a Pile of Wood instance."""
        pile_of_wood = PileOfWood(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.bulk_material],
        )

        pile_of_wood.actions.append(
            Play(card=pile_of_wood, player=player),
        )

        pile_of_wood.effects.append(
            ItemStats(
                name="Base stats",
                card=pile_of_wood,
                heft=2,
            ),
        )

        return pile_of_wood
