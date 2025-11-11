"""Create Compulsive Gatherer instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.card_class_def import CardClassDef as CardClassCommonDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.draw import Draw
from custom_tcg.core.dimension import CardClassDef, CardTypeDef
from custom_tcg.core.effect.activated import Activated
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play
from custom_tcg.feast_or_famine.card.dirty_blueberry import DirtyBlueberry

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, IPlayer


class CompulsiveGatherer(Card):
    """Create Compulsive Gatherer instances."""

    name: str = "Compulsive Gatherer"

    @classmethod
    def create(
        cls: type[CompulsiveGatherer],
        player: IPlayer,
    ) -> CompulsiveGatherer:
        """Create a Compulsive Gatherer instance."""
        compulsive_gatherer = CompulsiveGatherer(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassCommonDef.human],
        )

        compulsive_gatherer.actions.append(
            Play(card=compulsive_gatherer, player=player),
        )

        this_player: IPlayer = player

        draw: IAction = Draw(
            n=1,
            card=compulsive_gatherer,
            player=player,
        )

        find_dirty_blueberry: IAction = Find(
            finder=compulsive_gatherer,
            cards_to_find=[DirtyBlueberry],
            n=1,
            card=compulsive_gatherer,
            player=player,
            name="Forage",
        )

        compulsive_gatherer.actions.append(
            Activate(
                actions=[draw, find_dirty_blueberry],
                card=compulsive_gatherer,
                player=player,
                bind=lambda action, card, player: (
                    isinstance(action, Activate)
                    and CardClassDef.play in card.classes
                    and player is this_player
                    and not any(
                        isinstance(effect, Activated) for effect in card.effects
                    )
                ),
            ),
        )

        compulsive_gatherer.effects.append(
            BeingStats(
                name="Base stats",
                card=compulsive_gatherer,
                strength=1,
                dexterity=2,
                constitution=1,
                intelligence=1,
                wisdom=1,
                charisma=1,
            ),
        )

        return compulsive_gatherer
