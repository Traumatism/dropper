import os

from typer import Option, Argument, run

from ._core import Dropper


def main(
    file_path: str = Argument(
        ..., help="Path to the file to obfuscate",
        metavar="<path>",
        exists=True,
        dir_okay=False,
        readable=True
    ),
    junk_strings_len: int = Option(
        16, "--junk-strings-len", "-j", help="The length of the junk strings",
        metavar="<value>", min=4, max=32
    ),
    obfuscate_bools: bool = Option(
        True, "-nB", help="Don't obfuscate boolean values",
        flag_value=True, show_default=False
    ),
    obfuscate_ints: bool = Option(
        True, "-nI", help="Don't obfuscate integer values",
        flag_value=True, show_default=False
    ),
    obfuscate_strings: bool = Option(
        True, "-nS", help="Don't obfuscate string values",
        flag_value=True, show_default=False
    ),
    obfuscate_names: bool = Option(
        True, "-nN", help="Don't obfuscate function names",
        flag_value=True, show_default=False
    ),
) -> None:

    print("""

Dropper 🐍  Obfuscator
by @toastakerman

    """)

    with open(file_path, "r") as f:
        code = f.read()

    obfuscated = Dropper(
        code,
        junk_strings_lenght=junk_strings_len,
        obfuscate_bools=obfuscate_bools,
        obfuscate_ints=obfuscate_ints,
        obfuscate_strings=obfuscate_strings,
        obfuscate_names=obfuscate_names
    ).obfuscate()

    output_file = (
        f"obf_{file_path}"
        if "/" not in file_path
        and "\\" not in file_path
        else f"obf_{file_path.split(os.path.sep)[-1]}"
    )

    with open(output_file, "w") as f:
        f.write(obfuscated)


if __name__ == "__main__":
    run(main)
