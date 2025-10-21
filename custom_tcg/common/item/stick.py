"""Create Stick instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Stick(Card):
    """Create Stick instances."""

    name: str = "Stick"

    @classmethod
    def create(cls: type[Stick], player: IPlayer) -> Stick:
        """Create a Stick instance."""
        stick = Stick(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.base_material],
        )

        stick.actions.append(
            Play(card=stick, player=player),
        )

        stick.effects.append(
            ItemStats(
                name="Base stats",
                card=stick,
                heft=1,
            ),
        )

        return stick
