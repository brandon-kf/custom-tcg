"""A held effect."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.common.effect.interface import IHeld, IHolding
from custom_tcg.core.dimension import ActionStateDef, EffectStateDef
from custom_tcg.core.effect.effect import Effect
from custom_tcg.core.effect.remove_effect import RemoveEffect

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard, IExecutionContext


class Held(Effect, IHeld):
    """An effect showing that a card is held by another."""

    card_held_by: ICard
    paired_effect: IHolding
    remove_paired_effect: RemoveEffect

    def __init__(
        self: Held,
        card: ICard,
        card_held_by: ICard,
        card_holding_effect: IHolding,
    ) -> None:
        """Create a held effect."""
        super().__init__(
            name=f"Card '{card.name}' held by '{card_held_by.name}'",
            card=card,
        )
        self.card_held_by = card_held_by
        self.paired_effect = card_holding_effect
        self.remove_paired_effect = RemoveEffect(
            effect_to_remove=card_holding_effect,
            card_to_remove_from=card_held_by,
            card=card,
            player=card.player,
        )
        self.actions.append(self.remove_paired_effect)

    @override
    def deactivate(self: Held, context: IExecutionContext) -> None:
        super().deactivate(context=context)

        if self.paired_effect.state != EffectStateDef.inactive:
            context.execute(action=self.remove_paired_effect)
            self.remove_paired_effect.state = ActionStateDef.not_started
