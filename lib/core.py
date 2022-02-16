import zlib
import random
import base64
import tokenize

from .utils import (
    base64_string,
    string_to_hex,
    obfuscate_bool,
    obfuscate_int,
    obfuscate_string,
    xor_string,
    edit_token
)

from rich.console import Console


class Obfuscator:
    """ Obfuscate a file """

    class Obfuscated:
        """ Manage obfuscated code """

        def __init__(self):
            self.indent_level: int = 0
            self.__content: str = ""

        def add_line(self, line: str, end="\n") -> None:
            """ Add a line to the code """
            self.__content += ("    " * self.indent_level) + line + end

        @property
        def content(self) -> str:
            """ Return the content """
            return self.__content

    def __init__(self, file_name: str):
        self.console = Console()

        self.file = open(file_name, "r")

        with open(file_name, "r") as file:
            if "# hello from dwoppah" in file.read():
                self.console.print("Already obfuscated!")
                exit(0)

        self.generated_strings: list[str] = []

        self.primary_list = self.junk_string(3)
        self.eval = self.junk_string(5)
        self.exec = self.junk_string(5)
        self.splitted = self.junk_string(5)

        self.obfuscated = self.Obfuscated()

    def obfuscate_tokens(self) -> str:
        self.console.print("Tokenizing code...")

        _tokens = tokenize.generate_tokens(self.file.readline)

        tokens = []

        self.console.print("Obfuscating tokens...")

        for token in _tokens:

            if token.type in (61, 62):
                token = edit_token(token, "")

            if token.type == tokenize.STRING and token.string.startswith(
                ("'", "\"")
            ):
                key = random.randint(0, 10)
                obfuscated_key = obfuscate_int(key)

                encoded = xor_string(token.string[1:-1], key)
                b64_encoded = base64_string(encoded, _eval=self.eval)

                char = random.choice(("a", "b", "c", "ds"))

                real = (
                    f"(''.join(chr(ord({char})^{obfuscated_key})"
                    f"for({char})in({b64_encoded})))"
                )

                token = edit_token(token, real)

            if token.type == tokenize.NUMBER:
                token = edit_token(
                    token, obfuscate_int(int(token.string))
                )

            if (
                token.type == tokenize.NAME
                and token.string in ("False", "True")
            ):
                token = edit_token(
                    token, obfuscate_bool(eval(token.string), _bool=self.bool)
                )

            tokens.append(token)

        return tokenize.untokenize(tokens)

    def obfuscate(self):
        """ Obfuscate the code """

        self.console.print("Generating template...")

        self.obfuscated.add_line(
            f"{self.eval}=eval({obfuscate_string('eval')});"
        )

        obfuscated_exec = (
            f"{self.eval}({obfuscate_string('exec', _eval=self.eval)})"
        )

        self.obfuscated.add_line(f"{self.exec}={obfuscated_exec}")

        self.obfuscated.add_line(
            f"{self.primary_list}=["
            f"{self.eval}('{string_to_hex('None')}'),"
            f"{self.eval}('{string_to_hex('compile')}'),"
            f"{self.eval}('{string_to_hex('chr')}'),"
            f"{self.eval}('{string_to_hex('ord')}'),"
            f"{self.eval}('{string_to_hex('__import__')}'),"
            f"{self.eval}('{string_to_hex('bool')}')"
            "]",
            end=";"
        )

        self.none = f"{self.primary_list}[{obfuscate_int(0)}]"
        self.compile = f"{self.primary_list}[{obfuscate_int(1)}]"
        self.chr = f"{self.primary_list}[{obfuscate_int(2)}]"
        self.ord = f"{self.primary_list}[{obfuscate_int(3)}]"
        self.__import__ = f"{self.primary_list}[{obfuscate_int(4)}]"
        self.bool = f"{self.primary_list}[{obfuscate_int(5)}]"

        self.obfuscated.add_line(
            f"{self.exec}({obfuscate_string('import base64')})"
        )

        obfuscated_tokens = self.obfuscate_tokens()

        self.console.print("Splitting and re-organizating the code...")

        self.obfuscated.add_line(
            f"{self.splitted}="
            f"{self.eval}({obfuscate_string('str()', _eval=self.eval)})"
        )

        for part in map(lambda x: f"{x}\n", obfuscated_tokens.splitlines()):
            key = random.randint(0, 10)

            obfuscated_key = obfuscate_int(key)
            encoded = xor_string(part, key)
            b64_encoded = base64_string(encoded, _eval=self.eval)

            char = random.choice(("a", "b", "c", "d"))

            self.obfuscated.add_line(
                f"{self.splitted}+="
                f"''.join({self.chr}({self.ord}({char})^{obfuscated_key})"
                f"for({char})in({b64_encoded}))",
            )

        x = self.junk_string(5)

        self.obfuscated.add_line(
            f"{x}=["
            f"{self.splitted},"
            f"{obfuscate_string('<string>', _eval=self.eval)},"
            f"{obfuscate_string('exec', _eval=self.eval)}"
            "]"
        )

        self.obfuscated.add_line(f"{self.exec}({self.compile}(*{x}))")

    def junk_string(self, length: int = 10, b64: bool = False) -> str:
        """ Generate a random string of a given length """
        string = "".join(random.choice("Il") for _ in range(length))

        string = (
            self.junk_string(length, b64)
            if string in self.generated_strings else string
        )

        self.generated_strings.append(string)

        return (
            base64.b64encode(string.encode()).decode().replace("=", "")
            if base64 else string
        )

    def finalize(self) -> str:
        """ Finalize the code """

        self.console.print("Finalizing with zlib compression...")

        compressed = base64.b64encode(
            zlib.compress(self.obfuscated.content.encode())
        )

        final = '''""" (>,<)/ """
import zlib, base64

ENCODED = %s

# Decode the encoded string
COMPRESSED = base64.b64decode(ENCODED)

# Decompress the code
OBFUSCATED = zlib.decompress(COMPRESSED)

# Execute the code
exec(OBFUSCATED)

# hello from dwoppah
        '''[:-9] % compressed

        self.console.print(
            f"Final code size: {len(final):,} "
            "(This is very variable, restart the program to get another size)"
        )

        return final
