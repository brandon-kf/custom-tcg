"""Provide end-to-end test helpers for being activations."""

from custom_tcg.common.being.sheep import Sheep
from custom_tcg.common.effect.interface import IHeld
from custom_tcg.common.item.bundle_of_wool import BundleOfWool
from custom_tcg.common.item.cloth import Cloth
from custom_tcg.common.item.cord import Cord
from custom_tcg.common.item.extra_rations import ExtraRations
from custom_tcg.common.item.metal import Metal
from custom_tcg.common.item.pebble import Pebble
from custom_tcg.common.item.pelt import Pelt
from custom_tcg.common.item.stone import Stone
from custom_tcg.common.item.stone_path import StonePath
from custom_tcg.common.item.wood_structure import WoodStructure
from custom_tcg.core.game import Game
from custom_tcg.core.interface import ICard
from custom_tcg.core.util.e2e_test import (
    choose_by_name_contains,
    choose_option_n_then_confirm,
    choose_option_then_confirm,
    step_until_available,
)


def activate_desperate_shepherd(
    g: Game,
    separate: bool = False,  # noqa: FBT001, FBT002
    deliver: tuple[str, str] | None = None,
) -> None:
    """Activate Desperate Shepherd.

    Find sheep, shear, separate wool, deliver.
    """
    choose_by_name_contains(g, "Activate from card 'Desperate Shepherd'")

    # Search for sheep auto-resolves; no explicit choices.
    sheep = [c for c in g.context.player.played if isinstance(c, Sheep)]
    assert sheep, "Expected a Sheep to be found"

    # Shearing auto-executes via Tap (Select) + Find; no explicit choices.
    bundles = [
        c for c in g.context.player.played if isinstance(c, BundleOfWool)
    ]
    assert bundles, "Expected a Bundle of Wool to be created"
    held = next((e for e in bundles[0].effects if isinstance(e, IHeld)), None)
    assert held is not None
    assert held.card_held_by.name == "Desperate Shepherd"

    # If desired, Separate Ball of Wool (selector then cost), both via choices
    if separate:
        assert choose_option_then_confirm(
            g,
            "Select 'Ball of Wool'",
            max_steps=40,
        ), "Expected to select 'Ball of Wool' and confirm"
        # Then, verify a held Bundle of Wool (cost)
        assert choose_option_then_confirm(
            g,
            "Select 'Bundle of Wool'",
            max_steps=40,
        ), "Expected to select 'Bundle of Wool' and confirm"
    else:
        step_until_available(g, "Select 'Peasant'", max_steps=60)

    # If desired, Deliver Ball of Wool  (deliver action auto-prompts)
    if deliver is not None:
        receiver_name, item_name = deliver
        assert choose_option_then_confirm(
            g,
            f"Select '{receiver_name}'",
            max_steps=60,
        ), f"Expected to select '{receiver_name}' as receiver and confirm"
        assert choose_option_then_confirm(
            g,
            f"Select '{item_name}'",
            max_steps=60,
        ), f"Expected to select '{item_name}' to deliver and confirm"

    step_until_available(g, max_steps=60)


def activate_that_pebble_girl(
    g: Game,
    separate: type[ICard] | None = None,
    deliver: tuple[str, str] | None = None,
) -> None:
    """Activate That Pebble Girl: auto-collect a pile, optionally deliver it.

    The first action auto-creates a 'Pile of Rocks' via Find; no selection is
    required. If `deliver_to` is provided, deliver that pile to the receiver.
    """
    choose_by_name_contains(g, "Activate from card 'That Pebble Girl'")

    # Verify a Pile of Rocks was created and is held by That Pebble Girl
    piles = [c for c in g.context.player.played if c.name == "Pile of Rocks"]
    assert piles, "Expected a Pile of Rocks to be created"

    # If desired, Separate a base material (selector then cost), both via
    # choices
    if separate is not None and separate is Stone:
        assert choose_option_then_confirm(
            g,
            "Select 'Stone'",
            max_steps=40,
        ), "Expected to select 'Stone' and confirm"

    elif separate is not None and separate is Pebble:
        assert choose_option_then_confirm(
            g,
            "Select 'Pebble'",
            max_steps=40,
        ), "Expected to select 'Pebble' and confirm"

    if separate is not None:
        # Then, verify a held Pile of Rocks (cost)
        assert choose_option_then_confirm(
            g,
            "Select 'Pile of Rocks'",
            max_steps=40,
        ), "Expected to select 'Pile of Rocks' and confirm"
    else:
        step_until_available(g, "Select 'Peasant'", max_steps=60)

    # If desired, Deliver (deliver action auto-prompts)
    if deliver is not None:
        receiver_name, item_name = deliver
        assert choose_option_then_confirm(
            g,
            f"Select '{receiver_name}'",
            max_steps=60,
        ), f"Expected to select '{receiver_name}' as receiver and confirm"
        assert choose_option_then_confirm(
            g,
            f"Select '{item_name}'",
            max_steps=60,
        ), f"Expected to select '{item_name}' to deliver and confirm"

    step_until_available(g, max_steps=60)


def activate_early_architect(
    g: Game,
    build_stone_path: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """Activate Early Architect to build a Stone Path (requires 2 piles)."""
    choose_by_name_contains(g, "Activate from card 'Early Architect'")

    if build_stone_path:
        # Cost: select 2 Pile of Rocks held by the Early Architect
        assert choose_option_n_then_confirm(
            g,
            "Select 'Pile of Rocks'",
            2,
            max_steps=40,
        ), "Expected to select two 'Pile of Rocks' and confirm"

        # Verify Stone Path is created and not held (very heavy)
        stone_paths = [
            c for c in g.context.player.played if isinstance(c, StonePath)
        ]
        assert stone_paths, "Expected a Stone Path to be created"
        # Stone Path is heavy; shouldn't be held
        held_effects = [
            e for e in stone_paths[0].effects if hasattr(e, "card_held_by")
        ]
        assert not held_effects, "Stone Path should not be held after creation"

    step_until_available(g, max_steps=60)


def activate_apprentice_carpenter(
    g: Game,
    build_wood_structure: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """Activate Apprentice Carpenter to build a Wood Structure.

    Requires discarding two held Pile of Wood.
    """
    choose_by_name_contains(g, "Activate from card 'Apprentice Carpenter'")

    if build_wood_structure:
        assert choose_option_then_confirm(
            g,
            "Select 'Wood Structure'",
            max_steps=60,
        ), "Expected to select 'Wood Structure' and confirm"
        assert choose_option_n_then_confirm(
            g,
            "Select 'Pile of Wood'",
            2,
            max_steps=80,
        ), "Expected to select two 'Pile of Wood' for discard and confirm"

        structures = [
            c for c in g.context.player.played if isinstance(c, WoodStructure)
        ]
        assert structures, "Expected a Wood Structure to be created"

    step_until_available(g, max_steps=60)


def activate_questionable_butcher(
    g: Game,
    chop_chop: type[ICard] | None = None,
) -> None:
    """Activate Questionable Butcher to butcher a Peasant and get items."""
    choose_by_name_contains(
        g,
        "Activate from card 'Questionable Butcher'",
    )

    # Cost: select a being to butcher (choose Peasant)
    if chop_chop is not None:
        assert choose_option_then_confirm(
            g,
            option_name=f"Select '{chop_chop.name}'",
            max_steps=40,
        ), f"Expected to select '{chop_chop.name}' to butcher and confirm"

    step_until_available(g, max_steps=40)

    # Verify Extra Rations and Pelt are created and held by the butcher
    extra = [c for c in g.context.player.played if isinstance(c, ExtraRations)]
    pelt = [c for c in g.context.player.played if isinstance(c, Pelt)]
    assert extra, "Expected Extra Rations to be created"
    assert pelt, "Expected a Pelt to be created"

    def held_by(card_name: str) -> str | None:
        card = next(c for c in g.context.player.played if c.name == card_name)
        for e in card.effects:
            if hasattr(e, "card_held_by"):
                return e.card_held_by.name  # type: ignore[attr-defined]
        return None

    assert held_by("Extra Rations") == "Questionable Butcher", (
        "Extra Rations should be held by Questionable Butcher"
    )
    assert held_by("Pelt") == "Questionable Butcher", (
        "Pelt should be held by Questionable Butcher"
    )


def activate_apprentice_smith(
    g: Game,
    smelt_metal: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """Activate Apprentice Smith to smelt Metal by discarding rocks.

    Requires discarding two held Pile of Rocks.
    """
    choose_by_name_contains(g, "Activate from card 'Apprentice Smith'")

    if smelt_metal:
        assert choose_option_then_confirm(
            g,
            "Select 'Metal'",
            max_steps=60,
        ), "Expected to select 'Metal' and confirm"
        assert choose_option_n_then_confirm(
            g,
            "Select 'Pile of Rocks'",
            2,
            max_steps=80,
        ), "Expected to select two 'Pile of Rocks' for discard and confirm"

        metals = [c for c in g.context.player.played if isinstance(c, Metal)]
        assert metals, "Expected a Metal to be created"
        held = next(
            (e for e in metals[0].effects if isinstance(e, IHeld)),
            None,
        )
        assert held is not None
        assert held.card_held_by.name == "Apprentice Smith"

    step_until_available(g, max_steps=60)


def activate_seamstress(
    g: Game,
    find_cord: bool = False,  # noqa: FBT001, FBT002
    find_cloth: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """Activate Seamstress to find Cord and/or Cloth."""
    choose_by_name_contains(g, "Activate from card 'Seamstress'")

    if find_cord:
        # Choose to create Cord
        assert choose_option_then_confirm(
            g,
            "Select 'Cord'",
            max_steps=60,
        ), "Expected to select 'Cord' and confirm"
        # Discard Ball of Wool (cost)
        assert choose_option_then_confirm(
            g,
            "Select 'Ball of Wool'",
            max_steps=60,
        ), "Expected to select Ball of Wool to discard"

        cords = [c for c in g.context.player.played if isinstance(c, Cord)]
        assert cords, "Expected a Cord to be created"
        held = next((e for e in cords[0].effects if isinstance(e, IHeld)), None)
        assert held is not None
        assert held.card_held_by.name == "Seamstress"
    elif "Select 'Cord'" in [c.name for c in g.context.choices]:
        assert choose_option_then_confirm(
            g,
            "Cancel",
            max_steps=60,
        ), "Attempt to cancel Cord creation"

    if find_cloth:
        # Choose to create Cloth first (selector before cost per engine order)
        # Select 'Cloth' (some flows may re-prompt; try once more if needed)
        assert choose_option_then_confirm(
            g,
            "Select 'Cloth'",
            max_steps=60,
        ), "Expected to select 'Cloth' and confirm"
        success = choose_option_n_then_confirm(
            g,
            "Select 'Cord'",
            2,
            max_steps=80,
        )
        if not success:
            available = [c.name for c in g.context.choices]
            cords_all = [
                c for c in g.context.player.played if isinstance(c, Cord)
            ]
            held_cords = [
                c
                for c in cords_all
                for e in c.effects
                if isinstance(e, IHeld) and e.card_held_by.name == "Seamstress"
            ]
            msg = (
                "Expected to select two 'Cord' cards and confirm. "
                f"Choices: {available}; "
                f"cords_in_play={len(cords_all)}, "
                f"held_by_seamstress={len(held_cords)}"
            )
            raise AssertionError(msg)

        cloths = [c for c in g.context.player.played if isinstance(c, Cloth)]
        assert cloths, "Expected a Cloth to be created"
        held = next(
            (e for e in cloths[0].effects if isinstance(e, IHeld)),
            None,
        )
        assert held is not None
        assert held.card_held_by.name == "Seamstress"

    step_until_available(g, max_steps=60)


def activate_aimless_wanderer(
    g: Game,
    find_stick: bool = False,  # noqa: FBT001, FBT002
    find_trail: bool = False,  # noqa: FBT001, FBT002
    deliver: tuple[str, str] | None = None,
) -> None:
    """Activate Aimless Wanderer to find Stick and/or Trail."""
    choose_by_name_contains(g, "Activate from card 'Aimless Wanderer'")

    if find_stick:
        # Choose to create Stick
        assert choose_option_then_confirm(
            g,
            "Select 'Stick'",
            max_steps=60,
        ), "Expected to select 'Stick' and confirm"
        # Verify Pile of Wood (cost)
        assert choose_option_then_confirm(
            g,
            "Select 'Pile of Wood'",
            max_steps=60,
        ), "Expected to select Pile of Wood to verify"

        sticks = [c for c in g.context.player.played if c.name == "Stick"]
        assert sticks, "Expected a Stick to be created"
        held = next(
            (e for e in sticks[0].effects if isinstance(e, IHeld)),
            None,
        )
        assert held is not None
        assert held.card_held_by.name == "Aimless Wanderer"
    elif "Select 'Stick'" in [c.name for c in g.context.choices]:
        assert choose_option_then_confirm(
            g,
            "Cancel",
            max_steps=60,
        ), "Attempt to cancel Stick creation"

    if find_trail:
        # Choose to create Trail (selector before cost per engine order)
        # Select 'Trail' (some flows may re-prompt; try once more if needed)
        assert choose_option_then_confirm(
            g,
            "Select 'Trail'",
            max_steps=60,
        ), "Expected to select 'Trail' and confirm"
        assert choose_option_then_confirm(
            g,
            "Select 'Stick'",
            max_steps=60,
        ), "Expected to select Stick to Discard"

        trails = [c for c in g.context.player.played if c.name == "Trail"]
        assert trails, "Expected a Trail to be created"
        held = next(
            (e for e in trails[0].effects if isinstance(e, IHeld)),
            None,
        )
        assert held is None, "Trail should not be held after creation"
    elif "Select 'Trail'" in [c.name for c in g.context.choices]:
        assert choose_option_then_confirm(
            g,
            "Cancel",
            max_steps=60,
        ), "Attempt to cancel Trail creation"

    if deliver is not None:
        receiver_name, item_name = deliver
        assert choose_option_then_confirm(
            g,
            f"Select '{receiver_name}'",
            max_steps=60,
        ), f"Expected to select '{receiver_name}' as receiver and confirm"
        assert choose_option_then_confirm(
            g,
            f"Select '{item_name}'",
            max_steps=60,
        ), f"Expected to select '{item_name}' to deliver and confirm"

    step_until_available(g, max_steps=60)
