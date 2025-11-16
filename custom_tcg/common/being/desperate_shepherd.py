"""Create Desperate Shepherd instances."""

from __future__ import annotations

from secrets import randbelow
from typing import TYPE_CHECKING, cast

from custom_tcg.common.action.deliver import Deliver
from custom_tcg.common.action.find import Find
from custom_tcg.common.action.search import Search
from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.being.sheep import Sheep
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.ball_of_wool import BallOfWool
from custom_tcg.common.item.bundle_of_wool import BundleOfWool
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.select import Select
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.card.tap import Tap
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.effect.effect import Activated
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, IPlayer


class DesperateShepherd(Card):
    """Create Desperate Shepherd instances."""

    SHEEP_FOUND_ACCORDING_TO_ROLLED_VALUE: int = 6

    name: str = "Desperate Shepherd"

    @classmethod
    def create(
        cls: type[DesperateShepherd],
        player: IPlayer,
    ) -> DesperateShepherd:
        """Create a Desperate Shepherd instance."""
        desperate_shepherd = DesperateShepherd(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        search_for_sheep: IAction = Search(
            name=f"Search for {Sheep.name}",
            searcher=desperate_shepherd,
            cards_to_search_for=[Sheep],
            n=1,
            bind_success=lambda context: (  # noqa: ARG005
                randbelow(exclusive_upper_bound=6) + 1
                == DesperateShepherd.SHEEP_FOUND_ACCORDING_TO_ROLLED_VALUE
            ),
            card=desperate_shepherd,
            player=player,
        )

        shearing_tap_cost = Tap(
            cards_to_activate=Select(
                name=f"Tap sheared '{Sheep.name}'",
                options=lambda context: [
                    card
                    for card in context.player.played
                    if isinstance(card, Sheep)
                    and next(
                        (
                            effect
                            for effect in card.effects
                            if isinstance(effect, Activated)
                        ),
                        None,
                    )
                    is None
                ],
                card=desperate_shepherd,
                player=player,
            ),
            card=desperate_shepherd,
            player=player,
        )

        find_bundle_of_wool: IAction = Find(
            name=f"Shear a '{BundleOfWool.name}' from each sheep in play",
            finder=desperate_shepherd,
            cards_to_find=[BundleOfWool],
            bind_n=lambda context, card_factory: (  # noqa: ARG005
                len(
                    cast(
                        "Select",
                        shearing_tap_cost.cards_to_activate,
                    ).selected,
                )
            ),
            costs=[shearing_tap_cost],
            card=desperate_shepherd,
            player=player,
        )

        separate_a_base_material: IAction = Find(
            name=f"Separate a '{BallOfWool.name}' from '{BundleOfWool.name}'",
            finder=desperate_shepherd,
            cards_to_find=SelectByChoice(
                name=(
                    f"Separate a '{BallOfWool.name}' from '{BundleOfWool.name}'"
                ),
                accept_n=1,
                require_n=False,
                options=[BallOfWool],
                card=desperate_shepherd,
                player=player,
            ),
            costs=[
                SelectByHeld(
                    name=f"Verify '{BundleOfWool.name}' held",
                    held_type=BundleOfWool,
                    accept_n=1,
                    require_n=False,
                    auto_n=True,
                    card=desperate_shepherd,
                    player=player,
                ),
            ],
            card=desperate_shepherd,
            player=player,
        )

        deliver = Deliver(
            card=desperate_shepherd,
            player=player,
        )

        desperate_shepherd.actions.extend(
            (
                Play(card=desperate_shepherd, player=player),
                Activate(
                    actions=[
                        search_for_sheep,
                        find_bundle_of_wool,
                        separate_a_base_material,
                        deliver,
                    ],
                    card=desperate_shepherd,
                    player=player,
                ),
            ),
        )

        desperate_shepherd.effects.append(
            BeingStats(
                name="Base stats",
                card=desperate_shepherd,
                strength=1,
                dexterity=1,
                constitution=3,
                intelligence=1,
                wisdom=2,
                charisma=1,
            ),
        )

        return desperate_shepherd
