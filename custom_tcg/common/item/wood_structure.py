"""Create Wood Structure instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class WoodStructure(Card):
    """Create Wood Structure instances."""

    name: str = "Wood Structure"

    @classmethod
    def create(cls: type[WoodStructure], player: IPlayer) -> WoodStructure:
        """Create a Wood Structure instance."""
        wood_structure = WoodStructure(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.craft_material],
        )

        wood_structure.actions.append(
            Play(card=wood_structure, player=player),
        )

        wood_structure.effects.append(
            ItemStats(
                name="Base stats",
                card=wood_structure,
                heft=2,
                utility=1,
                uniquity=2,
            ),
        )

        return wood_structure
