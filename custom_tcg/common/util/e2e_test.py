"""Fixtures and utilities for end-to-end tests in the common module."""

from __future__ import annotations

import pytest

from custom_tcg.common.being import desperate_shepherd as ds_mod
from custom_tcg.common.being.peasant import Peasant
from custom_tcg.core import game as game_mod
from custom_tcg.core.anon import Deck, Player
from custom_tcg.core.game import Game
from custom_tcg.core.process.lets_play import LetsPlay
from custom_tcg.core.process.lets_rest import LetsRest
from custom_tcg.core.util import random as util_mod


@pytest.fixture
def game(monkeypatch: pytest.MonkeyPatch) -> Game:
    """Create a deterministic game instance for Shepherd/Seamstress flow."""

    def identity_randomize(*, ordered: list) -> list:
        return list(ordered)

    monkeypatch.setattr(util_mod, "list_randomize", identity_randomize)

    def fake_randbelow(*, exclusive_upper_bound: int) -> int:  # noqa: ARG001
        return 0

    # Keep turn order stable
    monkeypatch.setattr(game_mod, "randbelow", fake_randbelow)

    # Force Shepherd's search success: needs randbelow(6)+1 == 6
    def shepherd_randbelow(*, exclusive_upper_bound: int) -> int:  # noqa: ARG001
        return 5  # 5 + 1 == 6

    monkeypatch.setattr(ds_mod, "randbelow", shepherd_randbelow)

    # Players and starting decks
    p1 = Player(
        session_object_id="p1",
        name="Person 1",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )

    p1_deck = Deck(
        name="Deck 1",
        player=p1,
        starting=[
            LetsPlay.create(player=p1),
            LetsRest.create(player=p1),
            Peasant.create(player=p1),
        ],
        main=[],
    )
    p1.decks.append(p1_deck)
    p1.select_deck(deck=p1_deck)

    p2 = Player(
        session_object_id="p2",
        name="Person 2",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )

    p2_deck = Deck(
        name="Deck 2",
        player=p2,
        starting=[
            LetsPlay.create(player=p2),
            LetsRest.create(player=p2),
            Peasant.create(player=p2),
        ],
        main=[],
    )
    p2.decks.append(p2_deck)
    p2.select_deck(deck=p2_deck)

    return Game(players=[p1, p2])
