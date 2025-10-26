"""Tests for `custom_tcg.core.process.end_process` module."""

from unittest.mock import Mock

from custom_tcg.core.dimension import ActionStateDef, CardTypeDef
from custom_tcg.core.effect.effect import Effect
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.process.end_process import EndProcess


def _make_process_card(name: str, player, actions) -> Mock:  # noqa: ANN001
    card = Mock(name=f"{name}")
    card.name = name
    card.player = player
    card.types = [CardTypeDef.process]
    card.actions = actions
    card.effects = []
    card.register = Mock()
    return card


def test_end_process_queues_next_process_for_same_player() -> None:
    """Queue next process Activate in ready when not at end of list."""
    player = Mock(name="PlayerMock")
    player.processes = []

    # Create two process cards, each with a plain Activate action
    p1_act = Activate(
        card=Mock(register=Mock(), name="P1Card"),
        player=player,
        actions=[],
    )
    p2_act = Activate(
        card=Mock(register=Mock(), name="P2Card"),
        player=player,
        actions=[],
    )

    p1 = _make_process_card("P1", player, [p1_act])
    p2 = _make_process_card("P2", player, [p2_act])
    player.processes.extend([p1, p2])

    context = Mock(name="ExecutionContextMock")
    context.player = player
    context.players = [player]
    context.ready = []

    end = EndProcess(card=p1, player=player)
    end.enter(context=context)

    # Should have queued a Resolve for p2_act
    assert len(context.ready) == 1
    next_resolve = context.ready[0]
    assert getattr(next_resolve, "action", None) is p2_act
    assert next_resolve.state == ActionStateDef.queued


def test_end_process_rotates_to_next_player_and_clears_activated() -> None:
    """Rotate to next player and clear Activated effects on their processes."""
    p1 = Mock(name="P1")
    p2 = Mock(name="P2")
    p1.processes = []
    p2.processes = []

    # p2 has a process with an Activated effect and an Activate action
    p2_activate = Activate(
        card=Mock(register=Mock(), name="P2Card"),
        player=p2,
        actions=[],
    )
    p2_proc = _make_process_card("P2Proc", p2, [p2_activate])
    activated_effect = Effect(name="Activated", card=p2_proc)
    p2_proc.effects.append(activated_effect)
    p2.processes.append(p2_proc)

    # p1 current process
    p1_activate = Activate(
        card=Mock(register=Mock(), name="P1Card"),
        player=p1,
        actions=[],
    )
    p1_proc = _make_process_card("P1Proc", p1, [p1_activate])
    p1.processes.append(p1_proc)

    context = Mock(name="ExecutionContextMock")
    context.player = p1
    context.players = [p1, p2]
    context.ready = []

    end = EndProcess(card=p1_proc, player=p1)
    end.enter(context=context)

    # Should rotate to p2 and clear the Activated effect on their process
    assert context.player is p2
    assert all(e.name != "Activated" for e in p2_proc.effects)
    assert len(context.ready) == 1
    next_resolve = context.ready[0]
    assert getattr(next_resolve, "action", None) is p2_activate
    assert next_resolve.state == ActionStateDef.queued
