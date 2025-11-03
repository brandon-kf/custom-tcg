"""Create Destructive Darryl instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.action.find import Find
from custom_tcg.common.card_class_def import CardClassDef as CardClassCommonDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.holding import Holding
from custom_tcg.common.item.fire import Fire
from custom_tcg.common.item.flint import Flint
from custom_tcg.common.item.pile_of_wood import PileOfWood
from custom_tcg.core.card.card import Card
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.select import Select
from custom_tcg.core.dimension import CardClassDef, CardTypeDef
from custom_tcg.core.effect.effect import Activated
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play
from custom_tcg.core.interface import IPlayer

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, IPlayer


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

        find_flint_and_wood_unheld: list[IAction] = [
            Discard(
                name=f"Verify an unheld {Flint.name} is found",
                cards_to_discard=Select(
                    name=f"Strike a {Flint.name}",
                    n=1,
                    require_n=True,
                    options=lambda context: [
                        card
                        for card in context.player.played
                        if isinstance(card, Flint)
                        and next(
                            (
                                effect
                                for effect in card.effects
                                if isinstance(effect, Holding)
                            ),
                            None,
                        )
                        is None
                    ],
                    card=darryl,
                    player=player,
                ),
                card=darryl,
                player=player,
            ),
            Discard(
                name=f"Verify an unheld {PileOfWood.name} is found",
                cards_to_discard=Select(
                    name=f"Burn a {PileOfWood.name}",
                    n=1,
                    require_n=True,
                    options=lambda context: [
                        card
                        for card in context.player.played
                        if isinstance(card, PileOfWood)
                        and next(
                            (
                                effect
                                for effect in card.effects
                                if isinstance(effect, Holding)
                            ),
                            None,
                        )
                        is None
                    ],
                    card=darryl,
                    player=player,
                ),
                card=darryl,
                player=player,
            ),
        ]

        darryl.actions.append(
            Activate(
                actions=[
                    Find(
                        name=(
                            f"Start a '{Fire.name}' "
                            f"using '{Flint.name}' and a '{PileOfWood.name}'"
                        ),
                        finder=darryl,
                        cards_to_find=[Fire],
                        costs=find_flint_and_wood_unheld,
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
                        isinstance(effect, Activated)
                        for effect in darryl.effects
                    )
                ),
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
