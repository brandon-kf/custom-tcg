"""Create Cloth instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Cloth(Card):
    """Create Cloth instances."""

    name: str = "Cloth"

    @classmethod
    def create(cls: type[Cloth], player: IPlayer) -> Cloth:
        """Create a Pile of Wood instance."""
        cloth = Cloth(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.craft_material],
        )

        cloth.actions.append(
            Play(card=cloth, player=player),
        )

        cloth.effects.append(
            ItemStats(
                name="Base stats",
                card=cloth,
                heft=1,
                utility=2,
                uniquity=2,
            ),
        )

        return cloth
