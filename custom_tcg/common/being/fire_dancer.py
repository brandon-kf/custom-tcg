"""Create Fire Dancer instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.action.select_by_held import SelectByHeld
from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.burnable import Burnable
from custom_tcg.common.effect.burning import Burning
from custom_tcg.common.item.cloth import Cloth
from custom_tcg.common.item.fire import Fire
from custom_tcg.common.item.stick import Stick
from custom_tcg.common.item.torch import Torch
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.select import Select
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.effect.add_effect import AddEffect
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, IPlayer


class FireDancer(Card):
    """Create Fire Dancer instances."""

    name: str = "Fire Dancer"

    @classmethod
    def create(cls: type[FireDancer], player: IPlayer) -> FireDancer:
        """Create a Fire Dancer instance."""
        fire_dancer = FireDancer(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassDef.human],
        )

        fire_dancer.actions.append(
            Play(card=fire_dancer, player=player),
        )

        # Define activation actions.

        # Craft a torch.
        craft_torch: IAction = Find(
            name=f"Prepare a '{Torch.name}'",
            finder=fire_dancer,
            cards_to_find=SelectByChoice(
                name=(
                    f"Prepare a '{Torch.name}' from a "
                    f"'{Stick.name}' and some '{Cloth.name}'?"
                ),
                accept_n=1,
                require_n=False,
                options=[Torch],
                card=fire_dancer,
                player=player,
            ),
            costs=[
                Discard(
                    name=f"Shape the handle from '{Stick.name}'",
                    cards_to_discard=SelectByHeld(
                        name=f"Verify '{Stick.name}' is held",
                        held_type=Stick,
                        accept_n=1,
                        require_n=False,
                        card=fire_dancer,
                        player=player,
                    ),
                    card=fire_dancer,
                    player=player,
                ),
                Discard(
                    name=f"Wrap '{Cloth.name}'",
                    cards_to_discard=SelectByHeld(
                        name=f"Verify '{Cloth.name}' is held",
                        held_type=Cloth,
                        accept_n=1,
                        require_n=False,
                        card=fire_dancer,
                        player=player,
                    ),
                    card=fire_dancer,
                    player=player,
                ),
            ],
            card=fire_dancer,
            player=player,
        )

        # Tame fire.
        tame_fire: IAction = AddEffect(
            name="Tame a fire",
            effect_to_add=Burning,
            cards_affected=SelectByChoice(
                name="Select an item to hold fire",
                accept_n=1,
                require_n=False,
                options=lambda context: [
                    card
                    for card in context.player.played
                    for effect in card.effects
                    if isinstance(effect, Burnable)
                ],
                card=fire_dancer,
                player=player,
            ),
            costs=[
                Select(
                    name="Find an existing burning source",
                    options=lambda context: [
                        card
                        for card in context.player.played
                        for effect in card.effects
                        if isinstance(effect, Burning)
                    ],
                    n=1,
                    require_n=True,
                    card=fire_dancer,
                    player=player,
                ),
                Discard(
                    name="Tame a fire if one is found",
                    cards_to_discard=Select(
                        name="Tame a fire if one is found",
                        n=1,
                        require_n=False,
                        options=lambda context: [
                            card
                            for card in context.player.played
                            if isinstance(card, Fire)
                        ],
                        card=fire_dancer,
                        player=player,
                    ),
                    card=fire_dancer,
                    player=player,
                ),
            ],
            card=fire_dancer,
            player=player,
        )

        fire_dancer.actions.append(
            Activate(
                actions=[
                    craft_torch,
                    tame_fire,
                ],
                card=fire_dancer,
                player=player,
            ),
        )

        fire_dancer.effects.append(
            BeingStats(
                name="Base stats",
                card=fire_dancer,
                strength=2,
                dexterity=4,
                constitution=3,
                intelligence=2,
                wisdom=2,
                charisma=2,
            ),
        )

        return fire_dancer
