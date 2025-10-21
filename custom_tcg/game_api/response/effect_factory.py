"""Create effects of specific types for core objects."""

from custom_tcg.game_api.response.effect import Effect
from custom_tcg.game_api.response.held_effect import HeldEffect
from custom_tcg.game_api.response.holding_effect import HoldingEffect
from custom_tcg.common.effect.interface import IHeld, IHolding
from custom_tcg.core.interface import IEffect


class EffectFactory:
    """Create effects of specific types for core objects."""

    @staticmethod
    def parse(effect: IEffect) -> Effect:
        """Parse more specific effects if necessary."""
        parsed: Effect

        if isinstance(effect, IHolding):
            parsed = HoldingEffect(effect=effect)
        elif isinstance(effect, IHeld):
            parsed = HeldEffect(effect=effect)
        else:
            parsed = Effect(effect=effect)

        return parsed
