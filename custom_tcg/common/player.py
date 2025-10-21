"""Common implementations of players."""

from uuid import uuid4

from custom_tcg.common.being.aged_prophet import AgedProphet
from custom_tcg.common.being.aimless_wanderer import AimlessWanderer
from custom_tcg.common.being.apprentice_carpenter import ApprenticeCarpenter
from custom_tcg.common.being.apprentice_smith import ApprenticeSmith
from custom_tcg.common.being.desperate_shepherd import DesperateShepherd
from custom_tcg.common.being.destructive_darryl import DestructiveDarryl
from custom_tcg.common.being.early_architect import EarlyArchitect
from custom_tcg.common.being.peasant import Peasant
from custom_tcg.common.being.questionable_butcher import QuestionableButcher
from custom_tcg.common.being.resourceful_preacher import ResourcefulPreacher
from custom_tcg.common.being.seamstress import Seamstress
from custom_tcg.common.being.skilled_hunter import SkilledHunter
from custom_tcg.common.being.that_pebble_girl import ThatPebbleGirl
from custom_tcg.common.being.the_stewmaker import TheStewmaker
from custom_tcg.core.anon import Deck, Player
from custom_tcg.core.process.lets_play import LetsPlay
from custom_tcg.core.process.lets_rest import LetsRest
from custom_tcg.feast_or_famine.card.compulsive_gatherer import CompulsiveGatherer


def p1() -> Player:
    """Create a test player."""
    p1 = Player(
        session_object_id=uuid4().hex,
        name="Person 1",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )

    p1.decks.append(
        Deck(
            name="Deck 1",
            player=p1,
            starting=[
                LetsPlay.create(player=p1),
                LetsRest.create(player=p1),
                Peasant.create(player=p1),
            ],
            main=[
                *(AgedProphet.create(player=p1) for _ in range(1)),
                *(AimlessWanderer.create(player=p1) for _ in range(5)),
                *(ApprenticeCarpenter.create(player=p1) for _ in range(1)),
                *(ApprenticeSmith.create(player=p1) for _ in range(1)),
                *(DesperateShepherd.create(player=p1) for _ in range(5)),
                *(DestructiveDarryl.create(player=p1) for _ in range(1)),
                *(EarlyArchitect.create(player=p1) for _ in range(1)),
                *(Peasant.create(player=p1) for _ in range(5)),
                *(QuestionableButcher.create(player=p1) for _ in range(1)),
                *(ResourcefulPreacher.create(player=p1) for _ in range(1)),
                *(Seamstress.create(player=p1) for _ in range(1)),
                *(SkilledHunter.create(player=p1) for _ in range(1)),
                *(ThatPebbleGirl.create(player=p1) for _ in range(5)),
                *(TheStewmaker.create(player=p1) for _ in range(1)),
            ],
        ),
    )

    p1.select_deck(deck=p1.decks[0])

    return p1


def p2() -> Player:
    """Create another test player."""
    p2 = Player(
        session_object_id=uuid4().hex,
        name="Person 2",
        decks=[],
        starting_cards=[],
        main_cards=[],
        hand=[],
        processes=[],
        played=[],
        discard=[],
    )

    p2.decks.append(
        Deck(
            name="Deck 2",
            player=p2,
            starting=[
                LetsRest.create(player=p2),
                LetsPlay.create(player=p2),
                CompulsiveGatherer.create(player=p2),
            ],
            main=[
                *(DesperateShepherd.create(player=p2) for _ in range(20)),
            ],
        ),
    )

    p2.select_deck(deck=p2.decks[0])

    return p2
