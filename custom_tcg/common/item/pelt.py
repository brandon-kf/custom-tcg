"""Create Pelt instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Pelt(Card):
    """Create Pelt instances."""

    name: str = "Pelt"

    @classmethod
    def create(cls: type[Pelt], player: IPlayer) -> Pelt:
        """Create a Pelt instance."""
        pelt = Pelt(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.base_material],
        )

        pelt.actions.append(
            Play(card=pelt, player=player),
        )

        pelt.effects.append(
            ItemStats(
                name="Base stats",
                card=pelt,
                heft=1,
                uniquity=1,
            ),
        )

        return pelt
