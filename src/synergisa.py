import argparse
import base64
import json
from pathlib import Path
from typing import List, Tuple
from functools import cached_property
import pandas


from rich.console import Console
from rich.table import Table
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text
from rich import box
from loguru import logger

from save_layout import ShopBuys, ShopUpgrades, HepteractCrafts, SynergismConfig, SynergismGame

console = Console()

DATA_PATH = Path(__file__).parent.parent / "data"


def load_base64_file(file_path):
    with open(file_path, "rb") as file:
        encoded_data = file.read()
        decoded_data = base64.b64decode(encoded_data)
        return decoded_data


def print_balances(game: SynergismGame) -> List[Table]:
    misc_stats = Table(box=box.MINIMAL_DOUBLE_HEAD, title="Misc Items", title_style="bold")
    misc_stats.add_column("Stat")
    misc_stats.add_column("Value")

    misc_stats.add_row("C15 Exponent", f"{game.challenge15Exponent:.2e}")
    misc_stats.add_row("Overflux Orbs", f"{game.overfluxOrbs:.2e}")
    misc_stats.add_row("Overflux Powder", f"{game.overfluxPowder:.2e}")
    misc_stats.add_row("Singularity Count", f"{game.singularityCount:.0f}")

    cubes = Table(box=box.MINIMAL_DOUBLE_HEAD, title="Cubes", title_style="bold")

    cubes.add_column("Type")
    cubes.add_column("Amount")

    cubes.add_row("WoW Cubes", f"{game.wowCubes:.2e}")
    cubes.add_row("Tesseracts", f"{game.wowTesseracts:.2e}")
    cubes.add_row("Hypercubes", f"{game.wowHypercubes:.2e}")
    cubes.add_row("Platonic", f"{game.wowPlatonicCubes:.2e}")
    cubes.add_row("Hepteracts", f"{game.wowAbyssals:.2e}")


    hepts_table = Table(box=box.MINIMAL_DOUBLE_HEAD, title="Hepteracts", title_style="bold")

    hepts_table.add_column("Type")
    hepts_table.add_column("Tier")
    hepts_table.add_column("Balance")

    for hept_type in game.hepts.model_fields.keys():
        the_hept = getattr(game.hepts, hept_type)
        hepts_table.add_row(hept_type.title(), f"{the_hept.tier}", f"{the_hept.balance:.2e}")

    return [hepts_table, cubes, misc_stats]


def check_ratios(game: SynergismGame) -> Tuple[Table, List[str]]:
    ratios = Table(box=box.MINIMAL_DOUBLE_HEAD)
    ratios.add_column("Ratio")
    ratios.add_column("Value")

    chronos_accel_ratio = int(game.hepts.chronos.cap / game.hepts.accelerator.cap)
    chronos_challenge_ratio = int(game.hepts.chronos.cap / game.hepts.challenge.cap)
    hyper_challenge_ratio = int(game.hepts.hyperrealism.cap / game.hepts.challenge.cap)
    accel_mult_ratio = int(game.hepts.accelerator.cap / game.hepts.multiplier.cap)
    boost_mult_ratio = int(game.hepts.acceleratorBoost.cap / game.hepts.multiplier.cap)

    messages: List[str] = []

    e_chronos_accel = False
    e_chronos_challenge_hyper = False
    e_accel_mult_boost = False

    if chronos_accel_ratio != 32:
        messages.append(f"Chronos to Accelerator ratio is {chronos_accel_ratio:d} instead of 32")
        e_chronos_accel = True
    if chronos_challenge_ratio != 4:
        messages.append(f"Chronos to Challenge ratio is {chronos_challenge_ratio:d} instead of 4")
        e_chronos_challenge_hyper = True
    if hyper_challenge_ratio != 2:
        messages.append(f"Hyper to Challenge ratio is {hyper_challenge_ratio:d} instead of 2")
        e_chronos_challenge_hyper = True
    if accel_mult_ratio != 4:
        messages.append(f"Accel to Multiplier ratio is {accel_mult_ratio} instead of 4")
        e_accel_mult_boost = True
    if boost_mult_ratio != 2:
        messages.append(f"Boost to Multiplier ratio is {boost_mult_ratio} instead of 2")
        e_accel_mult_boost = True

    ratios.add_row("Chronos/Accel:", f"{'[bold red]' if e_chronos_accel else ''}{int(chronos_accel_ratio)}/1")
    ratios.add_row(
        "Chronos/Hyper/Challenge:",
        f"{'[bold red]' if e_chronos_challenge_hyper else ''}{chronos_challenge_ratio:d}/{hyper_challenge_ratio:d}/1",
    )
    ratios.add_row(
        "Accel/Boost/Mult:", f"{'[bold red]' if e_accel_mult_boost else ''}{accel_mult_ratio:d}/{boost_mult_ratio:d}/1"
    )

    return ratios, messages


def calculated_stats(game: SynergismGame) -> Table:
    stats = Table(title="Calculated Stats", box=box.MINIMAL_DOUBLE_HEAD)
    stats.add_column("Stat")
    stats.add_column("Value")

    stats.add_row("Chronos %:", f"{game.chronos_percent:.2f}%")
    stats.add_row("Chronos next %:", f"{game.chronos_percent_next:.2f}%")
    stats.add_row("Chronos increase:", f"{game.chronos_increase:.2f}%")
    stats.add_row("Chronos to level:", f"{game.hepts.chronos.to_level:.2e}", end_section=True)
    stats.add_row("Current multiplier:", f"{game.multiplier:.3f}")
    stats.add_row("RT ascension count:", f"{game.current_ascension_timer:.3f}")
    stats.add_row("Total quarks:", f"{game.total_quarks:d}")
    stats.add_row("Small hept inc:", f"{game.hepts_small_inc:.2f}")
    stats.add_row("Hept per day:", f"{game.hept_per_day:.2e}", end_section=True)
    stats.add_row("Orb to powder:", f"{game.orb_to_powder:.2f}")
    stats.add_row("%Cube from powder:", f"{game.cube_from_powder*100:.2f}%")
    stats.add_row("Powder goal:", f"{game.powder_goal:.2e}")
    stats.add_row("Orbs to powder goal:", f"{game.orbs_to_powder_goal:.2e}")

    return stats


def print_buys(buys: ShopBuys, game: SynergismGame) -> Table:
    buys_table = Table(box=box.MINIMAL_DOUBLE_HEAD, show_header=False)
    buys_table.add_column("", style="bold")
    buys_table.add_column("Item 1")
    buys_table.add_column("Item 2")
    buys_table.add_column("Benefit")
    
    buys_table.add_row("Accelrators", "Accel 1", "Accel 2", style="bold")
    buys_table.add_row("", f"{buys.accel1:d}", f"{buys.accel2:d}", f"{game.shop_benefit_accel}", end_section=True)

    buys_table.add_row("Wow Passes", "WoW 3", "WoW VY", style="bold")
    buys_table.add_row("", f"{buys.wow3:d}", f"{buys.wowY:d}", f"{game.shop_benefit_hept}")

    # console.print(Columns([accel_table, wow_table], equal=True))
    return buys_table


@logger.catch
def main() -> None:
    logger.opt(colors=True)

    parser = argparse.ArgumentParser(description="Decode a base64-encoded file.")
    parser.add_argument("file_path", help="path to the base64-encoded file")
    args = parser.parse_args()

    decoded_data = load_base64_file(args.file_path)

    parsed_data = json.loads(decoded_data)
    # print(json.dumps(parsed_data, indent=4, sort_keys=True))

    with open(f"{DATA_PATH}/inputs.json", "r") as file:
        game_config_json = json.load(file)

    game = SynergismGame(**parsed_data)
    conf = SynergismConfig(**game_config_json)

    game.set_config(conf)

    sd = pandas.read_excel(f"{DATA_PATH}/Data.xlsx", sheet_name="Shop", header=[0, 1], engine="openpyxl")
    buys = ShopBuys(sd, game.total_quarks)
    game.set_shop_benefits(buys)

    balances = print_balances(game)

    stats = calculated_stats(game)

    console.print(Columns(balances, equal=True))
    console.rule()
    console.print(stats)

    console.rule()
    ratios, messages = check_ratios(game)
    buys_table = print_buys(buys, game)

    console.print(Columns([ratios, buys_table], equal=True))

    if game.orbs_to_powder_goal <= 0:
        messages.append("Level Chronos!")
    else:
        messages.append("Dunno yet!")

    messages_print = Text("\n".join(messages))

    console.print(Panel(messages_print, title="Messages", box=box.DOUBLE, expand=False))


if __name__ == "__main__":
    main()
