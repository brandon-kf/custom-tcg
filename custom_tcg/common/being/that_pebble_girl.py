"""Create That Pebble Girl instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.deliver import Deliver
from custom_tcg.common.action.find import Find
from custom_tcg.common.action.search import Search
from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.flint import Flint
from custom_tcg.common.item.pebble import Pebble
from custom_tcg.common.item.pile_of_rocks import PileOfRocks
from custom_tcg.common.item.stone import Stone
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, IPlayer


class ThatPebbleGirl(Card):
    """Create That Pebble Girl instances."""

    FLINT_FOUND_ACCORDING_TO_N_PILES_OF_ROCKS: int = 3

    name: str = "That Pebble Girl"

    @classmethod
    def create(cls: type[ThatPebbleGirl], player: IPlayer) -> Card:
        """Create a That Pebble Girl instance."""
        that_pebble_girl = Card(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        find_pile_of_rocks: IAction = Find(
            name=f"Collect a '{PileOfRocks.name}'",
            finder=that_pebble_girl,
            cards_to_find=[PileOfRocks],
            n=1,
            card=that_pebble_girl,
            player=player,
        )

        search_for_flint: IAction = Search(
            name=f"Search for {Flint.name}",
            searcher=that_pebble_girl,
            cards_to_search_for=[Flint],
            n=1,
            card=that_pebble_girl,
            player=player,
            bind_success=lambda context: (
                sum(
                    (1 if isinstance(card, PileOfRocks) else 0)
                    for card in context.player.played
                )
                >= ThatPebbleGirl.FLINT_FOUND_ACCORDING_TO_N_PILES_OF_ROCKS
            ),
        )

        separate_a_base_material: IAction = Find(
            name="Separate a 'Stone' or 'Pebble' from 'Pile of Rocks'",
            finder=that_pebble_girl,
            cards_to_find=SelectByChoice(
                name="Select 'Stone' or 'Pebble'",
                accept_n=1,
                require_n=False,
                options=[Stone, Pebble],
                card=that_pebble_girl,
                player=player,
            ),
            costs=[
                SelectByHeld(
                    name=f"Verify {PileOfRocks.name} is held",
                    held_type=PileOfRocks,
                    accept_n=1,
                    require_n=True,
                    card=that_pebble_girl,
                    player=player,
                ),
            ],
            card=that_pebble_girl,
            player=player,
        )

        deliver = Deliver(
            card=that_pebble_girl,
            player=player,
        )

        that_pebble_girl.actions.extend(
            (
                Play(card=that_pebble_girl, player=player),
                Activate(
                    actions=[
                        find_pile_of_rocks,
                        search_for_flint,
                        separate_a_base_material,
                        deliver,
                    ],
                    card=that_pebble_girl,
                    player=player,
                ),
            ),
        )

        that_pebble_girl.effects.append(
            BeingStats(
                name="Base stats",
                card=that_pebble_girl,
                strength=2,
                dexterity=1,
                constitution=3,
                intelligence=1,
                wisdom=1,
                charisma=2,
            ),
        )

        return that_pebble_girl
