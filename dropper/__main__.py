import typer

from rich import print as _print

from .core import Dropper


def main(file_path: str) -> None:
    """ Dropper, a Python code obfuscator """
    _print("""

Dropper 🐍  Obfuscator
by @toastakerman

    """)

    with open(file_path, "r") as f:
        code = f.read()

    obfuscated = Dropper(code).obfuscate()

    with open(f"obf_{file_path}", "w") as f:
        f.write(obfuscated)


if __name__ == "__main__":
    typer.run(main)
