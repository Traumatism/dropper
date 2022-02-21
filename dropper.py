import argparse

from rich.console import Console

from lib.core import Obfuscator


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--file",
        help="The file to obfuscate",
        required=True,
        metavar="<path>",
        dest="file",
    )

    args = parser.parse_args()

    console = Console()
    console.print(f"Obfuscating '{args.file}'...")

    core = Obfuscator(args.file)
    core.obfuscate()

    print(core.finalize(), file=open("obf_" + args.file, "w"))

    console.print(f"Done, obfuscated file to 'obf_{args.file}' !")