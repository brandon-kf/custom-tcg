"""Create Extra Rations instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class ExtraRations(Card):
    """Create Extra Rations instances."""

    name: str = "Extra Rations"

    @classmethod
    def create(cls: type[ExtraRations], player: IPlayer) -> ExtraRations:
        """Create a Extra Rations instance."""
        extra_rations = ExtraRations(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.food, CardClassDef.simple_food],
        )

        extra_rations.actions.append(
            Play(card=extra_rations, player=player),
        )

        extra_rations.effects.append(
            ItemStats(
                name="Base stats",
                card=extra_rations,
                heft=1,
                utility=1,
            ),
        )

        return extra_rations
