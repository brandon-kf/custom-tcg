"""Create Seamstress instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.held_evaluator import HeldEvaluator
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.ball_of_wool import BallOfWool
from custom_tcg.common.item.cloth import Cloth
from custom_tcg.common.item.cord import Cord
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.selector import Selector
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Seamstress(Card):
    """Create Seamstress instances."""

    name: str = "Seamstress"

    @classmethod
    def create(cls: type[Seamstress], player: IPlayer) -> Seamstress:
        """Create a Peasant instance."""
        seamstress = Seamstress(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        seamstress.actions.append(
            Play(card=seamstress, player=player),
        )

        # Find Cord and Cloth, at a cost.
        seamstress.actions.append(
            Activate(
                actions=[
                    Find(
                        name=f"Wind fibers into '{Cord.name}'",
                        finder=seamstress,
                        cards_to_find=Selector(
                            name=f"Wind fibers into '{Cord.name}'?",
                            accept_n=lambda n: n == 1,
                            require_n=False,
                            options=[Cord],
                            card=seamstress,
                            player=player,
                        ),
                        costs=[
                            HeldEvaluator(
                                name=f"Discard a {BallOfWool.name}",
                                require_cards=BallOfWool,
                                require_n=1,
                                consume=True,
                                card=seamstress,
                                player=player,
                            ),
                        ],
                        card=seamstress,
                        player=player,
                    ),
                    Find(
                        name=f"Weave cords into '{Cloth.name}'",
                        finder=seamstress,
                        cards_to_find=Selector(
                            name=f"Weave cords into '{Cloth.name}'?",
                            accept_n=lambda n: n == 3,  # noqa: PLR2004
                            require_n=False,
                            options=[Cloth],
                            card=seamstress,
                            player=player,
                        ),
                        costs=[
                            HeldEvaluator(
                                name=f"Discard 3 {Cord.name}",
                                require_cards=Cord,
                                require_n=3,
                                consume=True,
                                card=seamstress,
                                player=player,
                            ),
                        ],
                        card=seamstress,
                        player=player,
                    ),
                ],
                card=seamstress,
                player=player,
            ),
        )

        seamstress.effects.append(
            BeingStats(
                name="Base stats",
                card=seamstress,
                strength=2,
                dexterity=3,
                constitution=2,
                intelligence=2,
                wisdom=3,
                charisma=3,
            ),
        )

        return seamstress
