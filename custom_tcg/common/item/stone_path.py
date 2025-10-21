"""Create Stone Path instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class StonePath(Card):
    """Create Stone Path instances."""

    name: str = "Stone Path"

    @classmethod
    def create(cls: type[StonePath], player: IPlayer) -> StonePath:
        """Create a Stone Path instance."""
        stone_path = StonePath(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.base_material],
        )

        stone_path.actions.append(
            Play(card=stone_path, player=player),
        )

        stone_path.effects.append(
            ItemStats(
                name="Base stats",
                card=stone_path,
                heft=1000,
                utility=3,
            ),
        )

        # TODO: Allow a vehicle to travel on this.  # noqa: FIX002, TD002, TD003
        # TODO: Connect to an opponent within range.  # noqa: E501, FIX002, TD002, TD003

        return stone_path
