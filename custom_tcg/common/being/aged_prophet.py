"""Create Aged Prophet instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.item.pebble import Pebble
from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.effect.add_effect import AddEffect
from custom_tcg.core.effect.effect import Activated
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class AgedProphet(Card):
    """Create Aged Prophet instances."""

    name: str = "Aged Prophet"

    @classmethod
    def create(cls: type[AgedProphet], player: IPlayer) -> AgedProphet:
        """Create a Peasant instance."""
        aged_prophet = AgedProphet(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        aged_prophet.actions.append(
            Play(card=aged_prophet, player=player),
        )

        this_player: IPlayer = player

        aged_prophet.actions.append(
            Activate(
                actions=[
                    AddEffect(
                        name=f"Admire a {Pebble.name}",
                        effect_to_add=BeingStats(
                            name="Wisdom of Admiration",
                            card=aged_prophet,
                            wisdom=1,
                        ),
                        card_to_add_to=aged_prophet,
                        card=aged_prophet,
                        player=player,
                    ),
                ],
                card=aged_prophet,
                player=player,
                bind=lambda action, card, player: (
                    isinstance(action, Activate)
                    and CardClassDef.rest in card.classes
                    and player is this_player
                    and not any(
                        isinstance(effect, Activated) for effect in card.effects
                    )
                ),
                costs=[
                    SelectByHeld(
                        name=f"Verify a '{Pebble.name}' is held",
                        held_type=Pebble,
                        accept_n=1,
                        require_n=False,
                        auto_n=True,
                        card=aged_prophet,
                        player=player,
                    ),
                ],
            ),
        )

        aged_prophet.effects.append(
            BeingStats(
                name="Base stats",
                card=aged_prophet,
                strength=1,
                dexterity=1,
                constitution=1,
                intelligence=2,
                wisdom=3,
                charisma=1,
            ),
        )

        return aged_prophet
