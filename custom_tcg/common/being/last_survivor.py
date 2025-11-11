"""Create Last Survivor instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef as CardClassCommonDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.draw import Draw
from custom_tcg.core.dimension import CardClassDef
from custom_tcg.core.dimension import CardTypeDef as CardTypeCommonDef
from custom_tcg.core.effect.activated import Activated
from custom_tcg.core.execution.activate import Activate

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class LastSurvivor(Card):
    """Create Last Survivor instances."""

    name: str = "Last Survivor"

    @classmethod
    def create(cls: type[LastSurvivor], player: IPlayer) -> LastSurvivor:
        """Create a Last Survivor instance."""
        last_survivor = LastSurvivor(
            name=cls.name,
            player=player,
            types=[CardTypeCommonDef.being],
            classes=[CardClassCommonDef.human],
        )

        this_player: IPlayer = player

        last_survivor.actions.append(
            Activate(
                actions=[
                    Draw(
                        n=3,
                        card=last_survivor,
                        player=player,
                    ),
                ],
                card=last_survivor,
                player=player,
                bind=lambda action, card, player: (
                    isinstance(action, Activate)
                    and CardClassDef.play in card.classes
                    and player is this_player
                    and not any(
                        isinstance(effect, Activated) for effect in card.effects
                    )
                ),
            ),
        )

        last_survivor.effects.append(
            BeingStats(
                name="Base stats",
                card=last_survivor,
                strength=3,
                dexterity=3,
                constitution=6,
                intelligence=3,
                wisdom=5,
                charisma=3,
            ),
        )

        return last_survivor
