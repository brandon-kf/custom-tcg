"""Create Questionable Butcher instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.deliver import Deliver
from custom_tcg.common.action.find import Find
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.extra_rations import ExtraRations
from custom_tcg.common.item.pelt import Pelt
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class QuestionableButcher(Card):
    """Create Questionable Butcher instances."""

    name: str = "Questionable Butcher"

    @classmethod
    def create(
        cls: type[QuestionableButcher],
        player: IPlayer,
    ) -> QuestionableButcher:
        """Create a Questionable Butcher instance."""
        butcher = QuestionableButcher(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        butcher.actions.append(
            Play(card=butcher, player=player),
        )

        # Find Cord and Cloth, at a cost.
        butcher.actions.append(
            Activate(
                actions=[
                    Find(
                        name="Chop chop",
                        finder=butcher,
                        cards_to_find=[ExtraRations, Pelt],
                        costs=[
                            Discard(
                                name="Select a being to butcher",
                                cards_to_discard=SelectByChoice(
                                    name="Select a being to butcher?",
                                    accept_n=1,
                                    require_n=False,
                                    options=lambda context: [
                                        card
                                        for card in context.player.played
                                        if CardTypeDef.being in card.types
                                        and card is not butcher
                                    ],
                                    card=butcher,
                                    player=player,
                                ),
                                card=butcher,
                                player=player,
                            ),
                        ],
                        card=butcher,
                        player=player,
                    ),
                    # Allow delivering items the butcher holds to other beings
                    Deliver(card=butcher, player=player),
                ],
                card=butcher,
                player=player,
            ),
        )

        butcher.effects.append(
            BeingStats(
                name="Base stats",
                card=butcher,
                strength=3,
                dexterity=2,
                constitution=3,
                intelligence=2,
                wisdom=3,
                charisma=3,
            ),
        )

        return butcher
