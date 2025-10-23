"""Create Apprentice Smith instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.metal import Metal
from custom_tcg.common.item.pile_of_rocks import PileOfRocks
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, IPlayer


class ApprenticeSmith(Card):
    """Create Apprentice Smith instances."""

    name: str = "Apprentice Smith"

    @classmethod
    def create(cls: type[ApprenticeSmith], player: IPlayer) -> ApprenticeSmith:
        """Create a Apprentice Smith instance."""
        smith = ApprenticeSmith(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        smith.actions.append(
            Play(card=smith, player=player),
        )

        smelt_rocks: IAction = Find(
            name=f"Smelt '{PileOfRocks.name}' into '{Metal.name}'",
            finder=smith,
            cards_to_find=SelectByChoice(
                name=(f"Smelt '{PileOfRocks.name}' into '{Metal.name}'?"),
                accept_n=1,
                require_n=False,
                options=[Metal],
                card=smith,
                player=player,
            ),
            costs=[
                Discard(
                    name=f"Smelt 2 '{PileOfRocks.name}'",
                    cards_to_discard=SelectByHeld(
                        name=f"Verify 2 copies of '{PileOfRocks.name}' is held",
                        held_type=PileOfRocks,
                        accept_n=2,
                        require_n=True,
                        card=smith,
                        player=player,
                    ),
                    card=smith,
                    player=player,
                ),
            ],
            card=smith,
            player=player,
        )

        # Find Metal, at a cost.
        smith.actions.append(
            Activate(
                actions=[smelt_rocks],
                card=smith,
                player=player,
            ),
        )

        smith.effects.append(
            BeingStats(
                name="Base stats",
                card=smith,
                strength=4,
                dexterity=2,
                constitution=4,
                intelligence=2,
                wisdom=2,
                charisma=2,
            ),
        )

        return smith
