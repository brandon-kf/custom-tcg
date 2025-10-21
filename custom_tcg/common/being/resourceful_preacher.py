"""Create Resourceful Preacher instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.held_evaluator import HeldEvaluator
from custom_tcg.common.card_class_def import CardClassDef, CardTypeCommonDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.draw import Draw
from custom_tcg.core.card.selector import Selector
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class ResourcefulPreacher(Card):
    """Create Resourceful Preacher instances."""

    name: str = "Resourceful Preacher"

    @classmethod
    def create(
        cls: type[ResourcefulPreacher],
        player: IPlayer,
    ) -> ResourcefulPreacher:
        """Create a Resourceful Preacher instance."""
        preacher = ResourcefulPreacher(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        preacher.actions.append(
            Play(card=preacher, player=player),
        )

        preacher.actions.append(
            Activate(
                actions=[
                    Draw(
                        n=1,
                        card=preacher,
                        player=player,
                        costs=[
                            HeldEvaluator(
                                name="Discard two items",
                                require_cards=Selector(
                                    name="Select two items?",
                                    accept_n=lambda n: n == 2,  # noqa: PLR2004
                                    require_n=False,
                                    options=lambda context: [
                                        card
                                        for card in context.player.played
                                        if CardTypeCommonDef.item in card.types
                                    ],
                                    card=preacher,
                                    player=player,
                                ),
                                require_n=2,
                                consume=True,
                                card=preacher,
                                player=player,
                            ),
                        ],
                    ),
                ],
                card=preacher,
                player=player,
            ),
        )

        preacher.effects.append(
            BeingStats(
                name="Base stats",
                card=preacher,
                strength=2,
                dexterity=2,
                constitution=2,
                intelligence=2,
                wisdom=2,
                charisma=2,
            ),
        )

        return preacher
