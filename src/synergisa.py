import argparse
import base64
import json

from loguru import logger
from munch import munchify


def load_base64_file(file_path):
    with open(file_path, "rb") as file:
        encoded_data = file.read()
        decoded_data = base64.b64decode(encoded_data)
        return decoded_data


def print_stats(save):
    print("Cubes \t\t")
    print(
        f"WoW {save.wowCubes:.2e} \t Tess {save.wowTesseracts:.2e} \t Hyper {save.wowHypercubes:.2e}"
    )

@logger.catch
def main():
    logger.opt(colors=True)

    parser = argparse.ArgumentParser(description="Decode a base64-encoded file.")
    parser.add_argument("file_path", help="path to the base64-encoded file")
    args = parser.parse_args()

    decoded_data = load_base64_file(args.file_path)

    parsed_data = json.loads(decoded_data)
    # print(json.dumps(parsed_data, indent=4, sort_keys=True))
    save = munchify(parsed_data)

    print_stats(save)

if __name__ == "__main__":
    main()
