"""Create Skilled Hunter instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.deliver import Deliver
from custom_tcg.common.action.find import Find
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.extra_rations import ExtraRations
from custom_tcg.common.item.pelt import Pelt
from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class SkilledHunter(Card):
    """Create Skilled Hunter instances."""

    name: str = "Skilled Hunter"

    @classmethod
    def create(cls: type[SkilledHunter], player: IPlayer) -> SkilledHunter:
        """Create a Skilled Hunter instance."""
        skilled_hunter = SkilledHunter(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        skilled_hunter.actions.append(
            Play(card=skilled_hunter, player=player),
        )

        skilled_hunter.actions.append(
            Activate(
                actions=[
                    Find(
                        name=f"Hunt prey for '{ExtraRations.name}'",
                        finder=skilled_hunter,
                        cards_to_find=[ExtraRations],
                        n=1,
                        card=skilled_hunter,
                        player=player,
                    ),
                    Find(
                        name=f"Process prey for '{Pelt.name}'",
                        finder=skilled_hunter,
                        cards_to_find=[Pelt],
                        n=1,
                        card=skilled_hunter,
                        player=player,
                    ),
                    Deliver(
                        card=skilled_hunter,
                        player=player,
                    ),
                ],
                card=skilled_hunter,
                player=player,
            ),
        )

        skilled_hunter.effects.append(
            BeingStats(
                name="Base stats",
                card=skilled_hunter,
                strength=2,
                dexterity=2,
                constitution=2,
                intelligence=2,
                wisdom=1,
                charisma=1,
            ),
        )

        return skilled_hunter
