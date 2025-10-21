"""Create Destructive Darryl instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.card_class_def import CardClassDef as CardClassCommonDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.interface import IHeld
from custom_tcg.common.item.fire import Fire
from custom_tcg.common.item.flint import Flint
from custom_tcg.common.item.pile_of_wood import PileOfWood
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.cost_evaluator import CostEvaluator
from custom_tcg.core.card.selector import Selector
from custom_tcg.core.dimension import CardClassDef, CardTypeDef
from custom_tcg.core.effect.effect import Activated
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play
from custom_tcg.core.interface import IPlayer

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class DestructiveDarryl(Card):
    """Create Destructive Darryl instances."""

    name: str = "Destructive Darryl"

    @classmethod
    def create(
        cls: type[DestructiveDarryl],
        player: IPlayer,
    ) -> DestructiveDarryl:
        """Create a Destructive Darryl instance."""
        darryl = DestructiveDarryl(
            name=cls.name,
            player=player,
            types=[CardTypeDef.being],
            classes=[CardClassCommonDef.human],
        )

        darryl.actions.append(
            Play(card=darryl, player=player),
        )

        this_player: IPlayer = player

        darryl.actions.append(
            Activate(
                actions=[
                    Find(
                        name=f"Start a '{Fire.name}'",
                        finder=darryl,
                        cards_to_find=[Fire],
                        card=darryl,
                        player=player,
                    ),
                ],
                card=darryl,
                player=player,
                bind=lambda action, card, player: (
                    isinstance(action, Activate)
                    and CardClassDef.play in card.classes
                    and player is this_player
                    and not any(
                        isinstance(effect, Activated) for effect in card.effects
                    )
                ),
                costs=[
                    CostEvaluator(
                        name=f"Spark a {Flint.name}",
                        require_cards=Selector(
                            name=f"Select a {Flint.name}",
                            accept_n=lambda n: n == 1,
                            require_n=True,
                            options=lambda context: [
                                card
                                for card in context.player.played
                                if isinstance(card, Flint)
                                and next(
                                    (
                                        effect
                                        for effect in card.effects
                                        if isinstance(effect, IHeld)
                                    ),
                                    None,
                                )
                                is None
                            ],
                            card=darryl,
                            player=player,
                        ),
                        require_n=1,
                        consume=True,
                        card=darryl,
                        player=player,
                    ),
                    CostEvaluator(
                        name=f"Burn a {PileOfWood.name}",
                        require_cards=Selector(
                            name=f"Select a {PileOfWood.name}",
                            accept_n=lambda n: n == 1,
                            require_n=True,
                            options=lambda context: [
                                card
                                for card in context.player.played
                                if isinstance(card, PileOfWood)
                                and next(
                                    (
                                        effect
                                        for effect in card.effects
                                        if isinstance(effect, IHeld)
                                    ),
                                    None,
                                )
                                is None
                            ],
                            card=darryl,
                            player=player,
                        ),
                        require_n=1,
                        consume=True,
                        card=darryl,
                        player=player,
                    ),
                ],
            ),
        )

        darryl.effects.append(
            BeingStats(
                name="Base stats",
                card=darryl,
                strength=5,
                dexterity=2,
                constitution=3,
                intelligence=1,
                wisdom=1,
                charisma=2,
            ),
        )

        return darryl
