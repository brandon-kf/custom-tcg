"""Create effects of specific types for core objects."""

from custom_tcg.common.effect.holding import Holding
from custom_tcg.core.interface import IEffect
from custom_tcg.game_api.response.effect import Effect
from custom_tcg.game_api.response.holding_effect import HoldingEffect


class EffectFactory:
    """Create effects of specific types for core objects."""

    @staticmethod
    def parse(effect: IEffect) -> Effect:
        """Parse more specific effects if necessary."""
        parsed: Effect

        if isinstance(effect, Holding):
            parsed = HoldingEffect(effect=effect)
        else:
            parsed = Effect(effect=effect)

        return parsed
