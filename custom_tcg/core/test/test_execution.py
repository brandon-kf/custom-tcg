"""Tests for `custom_tcg.core.execution.execution` module."""

from __future__ import annotations

from typing import Any

from custom_tcg.core.anon import Action as AnonAction
from custom_tcg.core.anon import Player as AnonPlayer
from custom_tcg.core.card.card import Card
from custom_tcg.core.dimension import CardClassDef, CardTypeDef
from custom_tcg.core.execution.execution import ExecutionContext


def test_execute_simple_action_completes_and_notifies() -> None:
    """Execute a simple action and convert notifications into Resolves."""
    # Build a minimal player and cards
    player = AnonPlayer(
        session_object_id="p1",
        name="P1",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )

    # Use real Card to satisfy register() calls from Action base class
    source_card = Card(
        name="Source",
        player=player,
        types=[CardTypeDef.process],
        classes=[CardClassDef.play],
    )
    notify_card = Card(
        name="NotifyCard",
        player=player,
        types=[],
        classes=[],
    )

    # Notify action whose card is in played so post_execute will include it
    notify_action = AnonAction(
        name="NotifyMe",
        card=notify_card,
        player=player,
        enter=lambda ctx: None,  # noqa: ARG005
    )

    player.played.append(notify_card)

    # The main action simply records that it executed
    executed: dict[str, Any] = {"count": 0}

    def on_enter(ctx) -> None:  # noqa: ANN001, ARG001
        executed["count"] += 1

    main_action = AnonAction(
        name="MainAction",
        card=source_card,
        player=player,
        enter=on_enter,
    )
    # Seed a notification to be converted into a Resolve during post_execute
    main_action.notify.append(notify_action)

    ctx = ExecutionContext(players=[player])

    ctx.execute(action=main_action)

    # Ensure the action's enter was invoked and the ready queue is empty
    assert executed["count"] == 1
    assert ctx.ready == []

    # A Resolve of notify_action should be queued to notifications
    assert any(
        getattr(n, "action", None) is notify_action for n in ctx.notifications
    )
