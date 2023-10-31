import argparse
import base64
import json
from pathlib import Path
from typing import List
from functools import cached_property
import pandas


from rich.console import Console
from rich.table import Table
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


def print_stats(game: SynergismGame) -> None:
    print(f"C15: {game.challenge15Exponent:.2e}")
    print("Cubes    >> ", end="")
    print(
        f"WoW {game.wowCubes:<16.2e} Tess {game.wowTesseracts:<16.2e} Hyper {game.wowHypercubes:<16.2e} Plat {game.wowHypercubes:.2e}"
    )

    print("Hept     >> ", end="")
    print(f"Chronos {game.hepts.chronos.balance:<12.2e} Abyss {game.hepts.abyss.balance:<16.2e}")

    print("Hept Tier>> ", end="")
    print(
        f"Chronos {game.hepts.chronos.tier:<12d} Abyss {game.hepts.abyss.tier:<16d} Accel {game.hepts.accelerator.tier:<16d}"
    )

    print("Overflux >> ", end="")
    print(f"Orbs {game.overfluxOrbs:.2e}\t Powder {game.overfluxPowder:.2e}")


def check_ratios(game: SynergismGame):
    print()
    ratios = Table(title="Ratios", box=box.MINIMAL_DOUBLE_HEAD)
    ratios.add_column("Ratio")
    ratios.add_column("Value")

    chronos_accel_ratio = int(game.hepts.chronos.cap / game.hepts.accelerator.cap)
    if chronos_accel_ratio != 32:
        print(f"Chronos to Accelerator ratio is {chronos_accel_ratio:d} instead of 32")
    ratios.add_row("Chronos/Accel:", f"{int(chronos_accel_ratio)}/1")

    chronos_challenge_ratio = int(game.hepts.chronos.cap / game.hepts.challenge.cap)
    hyper_challenge_ratio = int(game.hepts.hyperrealism.cap / game.hepts.challenge.cap)

    ratios.add_row("Chronos/Hyper/Challenge:", f"{chronos_challenge_ratio:d}/{hyper_challenge_ratio:d}/1")
    if chronos_challenge_ratio != 4:
        print(f"Chronos to Challenge ratio is {chronos_challenge_ratio:d} instead of 4")
    if hyper_challenge_ratio != 2:
        print(f"Hyper to Challenge ratio is {hyper_challenge_ratio:d} instead of 2")

    accel_mult_ratio = int(game.hepts.accelerator.cap / game.hepts.multiplier.cap)
    boost_mult_ratio = int(game.hepts.acceleratorBoost.cap / game.hepts.multiplier.cap)

    ratios.add_row("Accel/Boost/Mult:", f"{accel_mult_ratio:d}/{boost_mult_ratio:d}/1")
    if accel_mult_ratio != 4:
        print(f"Accel to Multiplier ratio is {accel_mult_ratio} instead of 4")
    if boost_mult_ratio != 2:
        print(f"Boost to Multiplier ratio is {boost_mult_ratio} instead of 2")

    console.print(ratios)


def calculated_stats(game: SynergismGame):
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

    console.print(stats)


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

    print_stats(game)

    sd = pandas.read_excel(f"{DATA_PATH}/Data.xlsx", sheet_name="Shop", header=[0, 1], engine="openpyxl")

    buys = ShopBuys(sd, game.total_quarks)

    # calculated_stats(game)
    # console.rule()
    # check_ratios(game)


if __name__ == "__main__":
    main()
