"""Create Torch instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Torch(Card):
    """Create Stone Path instances."""

    name: str = "Stone Path"

    @classmethod
    def create(cls: type[Torch], player: IPlayer) -> Torch:
        """Create a Torch instance."""
        torch = Torch(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.craft_material],
        )

        torch.actions.append(
            Play(card=torch, player=player),
        )

        torch.effects.append(
            ItemStats(
                name="Base stats",
                card=torch,
                heft=1,
                utility=2,
                uniquity=1,
            ),
        )

        return torch
