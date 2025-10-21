"""End the current process and queue up the next."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.resolve import Resolve
from custom_tcg.core.interface import IEffect

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard, IExecutionContext, IPlayer


class EndProcess(Action):
    """End the current process and queue up the next."""

    def __init__(
        self: EndProcess,
        card: ICard,
        player: IPlayer,
    ) -> None:
        """Create an End Process action."""
        super().__init__(
            name="End Process",
            card=card,
            player=player,
        )

    @override
    def enter(self: EndProcess, context: IExecutionContext) -> None:
        super().enter(context=context)

        current_process_index: int = context.player.processes.index(
            self.card,
        )
        next_process_index: int

        if current_process_index != len(context.player.processes) - 1:
            # Activate the next process for this player.
            next_process_index = current_process_index + 1

        else:
            # Move to next player and activate their first process.
            context.player = context.players[
                (context.players.index(context.player) + 1)
                % len(context.players)
            ]

            next_process_index = 0

            for process in context.player.processes:
                activated: IEffect | None = next(
                    (
                        effect
                        for effect in process.effects
                        if effect.name == "Activated"
                    ),
                    None,
                )
                if activated is not None:
                    process.effects.remove(activated)

        for action in context.player.processes[next_process_index].actions:
            action.reset_state()

        next_process_activation: Resolve = next(
            Resolve(action=action, card=action.card, player=action.player)
            for action in context.player.processes[next_process_index].actions
            if isinstance(action, Activate) and action.bind is None
        )

        next_process_activation.state = ActionStateDef.queued
        context.ready.append(next_process_activation)
