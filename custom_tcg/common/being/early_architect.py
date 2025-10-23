"""Create Early Architect instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.pile_of_rocks import PileOfRocks
from custom_tcg.common.item.stone_path import StonePath
from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class EarlyArchitect(Card):
    """Create Early Architect instances."""

    name: str = "Early Architect"

    @classmethod
    def create(cls: type[EarlyArchitect], player: IPlayer) -> EarlyArchitect:
        """Create a Early Architect instance."""
        early_architect = EarlyArchitect(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        early_architect.actions.append(
            Play(card=early_architect, player=player),
        )

        early_architect.actions.append(
            Activate(
                actions=[
                    Find(
                        name="Lay a stone path",
                        finder=early_architect,
                        cards_to_find=[StonePath],
                        n=1,
                        card=early_architect,
                        player=player,
                        costs=[
                            SelectByHeld(
                                name=f"Verify 2 {PileOfRocks.name} held",
                                held_type=PileOfRocks,
                                accept_n=2,
                                require_n=True,
                                card=early_architect,
                                player=player,
                            ),
                        ],
                    ),
                ],
                card=early_architect,
                player=player,
            ),
        )

        early_architect.effects.append(
            BeingStats(
                name="Base stats",
                card=early_architect,
                strength=1,
                dexterity=1,
                constitution=4,
                intelligence=2,
                wisdom=1,
                charisma=1,
            ),
        )

        return early_architect
