"""Create Flint instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Flint(Card):
    """Create Flint instances."""

    name: str = "Flint"

    @classmethod
    def create(cls: type[Flint], player: IPlayer) -> Flint:
        """Create a Flint instance."""
        flint = Flint(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.base_material],
        )

        flint.actions.append(
            Play(card=flint, player=player),
        )

        flint.effects.append(
            ItemStats(
                name="Base stats",
                card=flint,
                heft=1,
                utility=1,
                uniquity=1,
            ),
        )

        return flint
