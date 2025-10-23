"""Create Aimless Wanderer instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.deliver import Deliver
from custom_tcg.common.action.find import Find
from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.interface import IHeld
from custom_tcg.common.item.pile_of_wood import PileOfWood
from custom_tcg.common.item.stick import Stick
from custom_tcg.common.item.trail import Trail
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.select import Select
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, IPlayer


class AimlessWanderer(Card):
    """Create Aimless Wanderer instances."""

    name: str = "Aimless Wanderer"

    @classmethod
    def create(cls: type[AimlessWanderer], player: IPlayer) -> AimlessWanderer:
        """Create a Aimless Wanderer instance."""
        aimless_wanderer = AimlessWanderer(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        aimless_wanderer.actions.append(
            Play(card=aimless_wanderer, player=player),
        )

        # Define activation actions.

        # Must find a pile of wood.
        find_pile_of_wood: IAction = Find(
            name=f"Collect a '{PileOfWood.name}'",
            finder=aimless_wanderer,
            cards_to_find=[PileOfWood],
            n=1,
            card=aimless_wanderer,
            player=player,
        )

        # Can separate one or fewer sticks.
        separate_a_base_material: IAction = Find(
            name=f"Separate a '{Stick.name}' from '{PileOfWood.name}'",
            finder=aimless_wanderer,
            cards_to_find=SelectByChoice(
                name=f"Separate a '{Stick.name}' from '{PileOfWood.name}'",
                accept_n=1,
                require_n=False,
                options=[Stick],
                card=aimless_wanderer,
                player=player,
            ),
            costs=[
                Select(
                    name=f"Verify '{PileOfWood.name}' is held",
                    options=lambda context: [
                        card
                        for card in context.player.played
                        for effect in card.effects
                        if isinstance(card, PileOfWood)
                        and isinstance(effect, IHeld)
                        and effect.card_held_by == aimless_wanderer
                    ],
                    n=1,
                    require_n=True,
                    card=aimless_wanderer,
                    player=player,
                ),
            ],
            card=aimless_wanderer,
            player=player,
        )

        # Can discover a trail.
        discover_a_trail: IAction = Find(
            name=f"Discover a '{Trail.name}'",
            finder=aimless_wanderer,
            cards_to_find=SelectByChoice(
                name=f"Create a '{Trail.name}'?",
                accept_n=1,
                require_n=False,
                options=[Trail],
                card=aimless_wanderer,
                player=player,
            ),
            costs=[
                Discard(
                    name=f"Mark the trailhead with a '{Stick.name}'",
                    cards_to_discard=SelectByHeld(
                        name=f"Verify '{Stick.name}' is held",
                        held_type=Stick,
                        accept_n=1,
                        require_n=True,
                        card=aimless_wanderer,
                        player=player,
                    ),
                    card=aimless_wanderer,
                    player=player,
                ),
            ],
            card=aimless_wanderer,
            player=player,
        )

        # Can deliver an item currently holding.
        deliver: IAction = Deliver(
            card=aimless_wanderer,
            player=player,
        )

        aimless_wanderer.actions.append(
            Activate(
                actions=[
                    find_pile_of_wood,
                    separate_a_base_material,
                    discover_a_trail,
                    deliver,
                ],
                card=aimless_wanderer,
                player=player,
            ),
        )

        aimless_wanderer.effects.append(
            BeingStats(
                name="Base stats",
                card=aimless_wanderer,
                strength=1,
                dexterity=2,
                constitution=3,
                intelligence=1,
                wisdom=1,
                charisma=2,
            ),
        )

        return aimless_wanderer
