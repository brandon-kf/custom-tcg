"""Create Apprentice Carpenter instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.held_evaluator import HeldEvaluator
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.pile_of_wood import PileOfWood
from custom_tcg.common.item.wood_structure import WoodStructure
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.selector import Selector
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class ApprenticeCarpenter(Card):
    """Create Apprentice Carpenter instances."""

    name: str = "Apprentice Carpenter"

    @classmethod
    def create(
        cls: type[ApprenticeCarpenter],
        player: IPlayer,
    ) -> ApprenticeCarpenter:
        """Create a Apprentice Carpenter instance."""
        carp = ApprenticeCarpenter(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        carp.actions.append(
            Play(card=carp, player=player),
        )

        # Find Cord and Cloth, at a cost.
        carp.actions.append(
            Activate(
                actions=[
                    Find(
                        name=f"Construct a '{WoodStructure.name}'",
                        finder=carp,
                        cards_to_find=Selector(
                            name=f"Construct a '{WoodStructure.name}'?",
                            accept_n=lambda n: n == 1,
                            require_n=False,
                            options=[WoodStructure],
                            card=carp,
                            player=player,
                        ),
                        costs=[
                            HeldEvaluator(
                                name=(
                                    f"Discard two copies of "
                                    f"'{PileOfWood.name}'"
                                ),
                                require_cards=PileOfWood,
                                require_n=2,
                                consume=True,
                                card=carp,
                                player=player,
                            ),
                        ],
                        card=carp,
                        player=player,
                    ),
                ],
                card=carp,
                player=player,
            ),
        )

        carp.effects.append(
            BeingStats(
                name="Base stats",
                card=carp,
                strength=2,
                dexterity=3,
                constitution=4,
                intelligence=3,
                wisdom=2,
                charisma=2,
            ),
        )

        return carp
