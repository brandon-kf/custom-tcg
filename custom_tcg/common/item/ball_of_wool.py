"""Create Ball of Wool instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class BallOfWool(Card):
    """Create Ball of Wool instances."""

    name: str = "Ball of Wool"

    @classmethod
    def create(cls: type[BallOfWool], player: IPlayer) -> BallOfWool:
        """Create a Ball of Wool instance."""
        ball_of_wool: Card = BallOfWool(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.base_material],
        )

        ball_of_wool.actions.append(
            Play(card=ball_of_wool, player=player),
        )

        ball_of_wool.effects.append(
            ItemStats(
                name="Base stats",
                card=ball_of_wool,
                heft=1,
            ),
        )

        return ball_of_wool
