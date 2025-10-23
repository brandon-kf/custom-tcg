"""Create The Stewmaker instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.interface import IHeld
from custom_tcg.common.item.stew import Stew
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class TheStewmaker(Card):
    """Create The Stewmaker instances."""

    name: str = "The Stewmaker"

    @classmethod
    def create(
        cls: type[TheStewmaker],
        player: IPlayer,
    ) -> TheStewmaker:
        """Create a The Stewmaker instance."""
        stew = TheStewmaker(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        stew.actions.append(
            Play(card=stew, player=player),
        )

        # Find Cord and Cloth, at a cost.
        stew.actions.append(
            Activate(
                actions=[
                    Find(
                        name=f"Cook a '{Stew.name}'",
                        finder=stew,
                        cards_to_find=SelectByChoice(
                            name=f"Cook a '{Stew.name}'?",
                            accept_n=1,
                            require_n=False,
                            options=[Stew],
                            card=stew,
                            player=player,
                        ),
                        costs=[
                            Discard(
                                name="Discard two food items",
                                cards_to_discard=SelectByChoice(
                                    name="Cook two food items",
                                    accept_n=2,
                                    require_n=True,
                                    options=lambda context: [
                                        card
                                        for card in context.player.played
                                        if CardClassDef.food in card.classes
                                        and next(
                                            (
                                                effect
                                                for effect in card.effects
                                                if isinstance(effect, IHeld)
                                            ),
                                            None,
                                        )
                                        is None
                                    ],
                                    card=stew,
                                    player=player,
                                ),
                                card=stew,
                                player=player,
                            ),
                        ],
                        card=stew,
                        player=player,
                    ),
                ],
                card=stew,
                player=player,
            ),
        )

        stew.effects.append(
            BeingStats(
                name="Base stats",
                card=stew,
                strength=2,
                dexterity=2,
                constitution=3,
                intelligence=2,
                wisdom=3,
                charisma=4,
            ),
        )

        return stew
