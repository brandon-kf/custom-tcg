"""Create Apprentice Smith instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.held_evaluator import HeldEvaluator
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.metal import Metal
from custom_tcg.common.item.pile_of_rocks import PileOfRocks
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.selector import Selector
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class ApprenticeSmith(Card):
    """Create Apprentice Smith instances."""

    name: str = "Apprentice Smith"

    @classmethod
    def create(cls: type[ApprenticeSmith], player: IPlayer) -> ApprenticeSmith:
        """Create a Apprentice Smith instance."""
        smith = ApprenticeSmith(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        smith.actions.append(
            Play(card=smith, player=player),
        )

        # Find Cord and Cloth, at a cost.
        smith.actions.append(
            Activate(
                actions=[
                    Find(
                        name=f"Smelt '{PileOfRocks.name}' into '{Metal.name}'",
                        finder=smith,
                        cards_to_find=Selector(
                            name=(
                                f"Smelt '{PileOfRocks.name}' "
                                f"into '{Metal.name}'?"
                            ),
                            accept_n=lambda n: n == 1,
                            require_n=False,
                            options=[Metal],
                            card=smith,
                            player=player,
                        ),
                        costs=[
                            HeldEvaluator(
                                name=(
                                    f"Discard two copies of "
                                    f"'{PileOfRocks.name}'"
                                ),
                                require_cards=PileOfRocks,
                                require_n=2,
                                consume=True,
                                card=smith,
                                player=player,
                            ),
                        ],
                        card=smith,
                        player=player,
                    ),
                ],
                card=smith,
                player=player,
            ),
        )

        smith.effects.append(
            BeingStats(
                name="Base stats",
                card=smith,
                strength=4,
                dexterity=2,
                constitution=4,
                intelligence=2,
                wisdom=2,
                charisma=2,
            ),
        )

        return smith
