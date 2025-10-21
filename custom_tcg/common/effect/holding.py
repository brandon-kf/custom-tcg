"""A holding effect."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.common.action.drop import Drop
from custom_tcg.common.effect.held import Held, IHolding
from custom_tcg.core.dimension import ActionStateDef, EffectStateDef
from custom_tcg.core.effect.add_effect import AddEffect
from custom_tcg.core.effect.effect import Effect
from custom_tcg.core.effect.remove_effect import RemoveEffect

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard, IExecutionContext


class Holding(Effect, IHolding):
    """An effect showing that a card is holding another."""

    card_holding: ICard
    paired_effect: Held
    add_paired_effect: AddEffect
    remove_paired_effect: RemoveEffect
    drop: Drop

    def __init__(
        self: Holding,
        card: ICard,
        card_holding: ICard,
    ) -> None:
        """Create a holding effect."""
        super().__init__(
            name=f"Card '{card.name}' holding '{card_holding.name}'",
            card=card,
        )
        self.card_holding = card_holding
        self.paired_effect = Held(
            card=card_holding,
            card_held_by=card,
            card_holding_effect=self,
        )
        self.add_paired_effect = AddEffect(
            effect_to_add=self.paired_effect,
            card_to_add_to=card_holding,
            card=card,
            player=card.player,
        )
        self.remove_paired_effect = RemoveEffect(
            effect_to_remove=self.paired_effect,
            card_to_remove_from=card_holding,
            card=card,
            player=card.player,
        )
        self.drop = Drop(
            card_to_drop=card_holding,
            card=card,
            player=card.player,
        )
        self.actions.extend(
            (
                self.add_paired_effect,
                self.remove_paired_effect,
                self.drop,
            ),
        )

    @override
    def activate(self: Holding, context: IExecutionContext) -> None:
        super().activate(context=context)

        context.execute(action=self.add_paired_effect)
        self.add_paired_effect.state = ActionStateDef.not_started

        self.card.actions.append(self.drop)

    @override
    def deactivate(self: Holding, context: IExecutionContext) -> None:
        super().deactivate(context=context)

        if self.paired_effect.state != EffectStateDef.inactive:
            context.execute(action=self.remove_paired_effect)
            self.remove_paired_effect.state = ActionStateDef.not_started

        self.card.actions.remove(self.drop)
