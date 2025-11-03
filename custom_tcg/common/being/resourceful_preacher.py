"""Create Resourceful Preacher instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.holding import Holding
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.draw import Draw
from custom_tcg.core.card.select_by_choice import SelectByChoice
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

        # TODO: Transfer ownership of items? Make them holy by adding an effect to them?  # noqa: E501, FIX002, TD002, TD003
        preacher.actions.append(
            Activate(
                actions=[
                    Draw(
                        name="Become a fisher of people",
                        n=1,
                        card=preacher,
                        player=player,
                        costs=[
                            Discard(
                                name="Discard two items",
                                cards_to_discard=SelectByChoice(
                                    name="Gift two holy symbols to a stranger?",
                                    accept_n=2,
                                    require_n=False,
                                    options=lambda context: [
                                        card
                                        for card in context.player.played
                                        for effect in card.effects
                                        if isinstance(effect, Holding)
                                        and effect.card_held is preacher
                                    ],
                                    card=preacher,
                                    player=player,
                                ),
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
                intelligence=3,
                wisdom=2,
                charisma=4,
            ),
        )

        return preacher
