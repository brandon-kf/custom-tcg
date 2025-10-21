"""Create Bundle of Wool instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class BundleOfWool(Card):
    """Create Bundle of Wool instances."""

    name: str = "Bundle of Wool"

    @classmethod
    def create(cls: type[BundleOfWool], player: IPlayer) -> BundleOfWool:
        """Create a Bundle of Wool instance."""
        bundle_of_wool: Card = BundleOfWool(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.bulk_material],
        )

        bundle_of_wool.actions.append(
            Play(card=bundle_of_wool, player=player),
        )

        bundle_of_wool.effects.append(
            ItemStats(
                name="Base stats",
                card=bundle_of_wool,
                heft=2,
            ),
        )

        return bundle_of_wool
