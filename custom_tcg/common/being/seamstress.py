"""Create Seamstress instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.ball_of_wool import BallOfWool
from custom_tcg.common.item.cloth import Cloth
from custom_tcg.common.item.cord import Cord
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, IPlayer


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

        # Can craft Cord from a ball of wool.
        find_cord: IAction = Find(
            name=f"Wind fibers into '{Cord.name}'",
            finder=seamstress,
            cards_to_find=SelectByChoice(
                name=f"Wind fibers into '{Cord.name}'?",
                accept_n=1,
                require_n=False,
                options=[Cord],
                card=seamstress,
                player=player,
            ),
            costs=[
                Discard(
                    name=f"Discard a {BallOfWool.name}",
                    cards_to_discard=SelectByHeld(
                        name=f"Verify {BallOfWool.name} is held",
                        held_type=BallOfWool,
                        accept_n=1,
                        require_n=False,
                        auto_n=True,
                        card=seamstress,
                        player=player,
                    ),
                    card=seamstress,
                    player=player,
                ),
            ],
            card=seamstress,
            player=player,
        )

        # Can craft Cloth from two cords.
        find_cloth: IAction = Find(
            name=f"Weave cords into '{Cloth.name}'",
            finder=seamstress,
            cards_to_find=SelectByChoice(
                name=f"Weave cords into '{Cloth.name}'?",
                accept_n=1,
                require_n=False,
                options=[Cloth],
                card=seamstress,
                player=player,
            ),
            costs=[
                Discard(
                    name=f"Discard 2 copies of '{Cord.name}'",
                    cards_to_discard=SelectByHeld(
                        name=f"Verify 2 copies of {Cord.name} held",
                        held_type=Cord,
                        accept_n=2,
                        require_n=False,
                        auto_n=True,
                        card=seamstress,
                        player=player,
                    ),
                    card=seamstress,
                    player=player,
                ),
            ],
            card=seamstress,
            player=player,
        )

        # Find Cord and Cloth, at a cost.
        seamstress.actions.append(
            Activate(
                actions=[find_cord, find_cloth],
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
                constitution=4,
                intelligence=2,
                wisdom=3,
                charisma=3,
            ),
        )

        return seamstress
