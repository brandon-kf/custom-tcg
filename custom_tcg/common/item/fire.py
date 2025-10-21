"""Create Fire instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Fire(Card):
    """Create Fire instances."""

    name: str = "Fire"

    @classmethod
    def create(cls: type[Fire], player: IPlayer) -> Fire:
        """Create a Fire instance."""
        fire = Fire(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.base_material],
        )

        fire.actions.append(
            Play(card=fire, player=player),
        )

        fire.effects.append(
            ItemStats(
                name="Base stats",
                card=fire,
                heft=1000,
            ),
        )

        # TODO: Make this spread unless controlled.  # noqa: TD002, FIX002, TD003, E501

        return fire
