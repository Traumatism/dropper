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
    generate_xor_key,
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

        self.eval = self.junk_string(3)
        self.exec = self.junk_string(3)

        self.comp = self.junk_string(3)
        self.none = self.junk_string(3)

        self.ord = self.junk_string(3)
        self.chr = self.junk_string(3)

        self.splitted = self.junk_string(3)

        self.obfuscated = self.Obfuscated()
        self.ident_level: int = 0

    def obfuscate_tokens(self) -> str:
        self.console.print("Tokenizing code...")

        _tokens = tokenize.generate_tokens(self.file.readline)

        tokens = []

        self.console.print("Obfuscating tokens...")

        for token in _tokens:

            if token.type in (61, 62):
                token = edit_token(token, "")

            if token.type == 3:
                key = generate_xor_key()
                encoded = xor_string(token.string[1:-1], key)
                obfuscated_key = obfuscate_int(key)

                real = (
                    f"(''.join(chr(ord(char)^{obfuscated_key}) "
                    f"for char in {base64_string(encoded)}))"
                )

                token = edit_token(token, real)

            if token.type == 2:
                token = edit_token(
                    token, obfuscate_int(int(token.string), range=(1, 3))
                )

            if token.type == 1 and token.string in ("False", "True"):
                token = edit_token(token, obfuscate_bool(eval(token.string)))

            tokens.append(token)

        return tokenize.untokenize(tokens)

    def obfuscate(self):
        """Obfuscate the code"""

        self.console.print("Generating template...")

        self.obfuscated.add_line(
            f"{self.eval}=eval({obfuscate_string('eval')});"
        )

        obfuscated_exec = f"{self.eval}({obfuscate_string('exec')})"

        self.obfuscated.add_line(f"{self.exec}={obfuscated_exec}")
        self.obfuscated.add_line("\n")

        self.obfuscated.add_line(
            f"{self.none},{self.comp},{self.chr},{self.ord}"
            "="
            f"{self.eval}('{string_to_hex('None')}')"
            ","
            f"{self.eval}('{string_to_hex('compile')}')"
            ","
            f"{self.eval}('{string_to_hex('chr')}')"
            ","
            f"{self.eval}('{string_to_hex('ord')}')",
            end=";"
        )

        obfuscated_tokens = self.obfuscate_tokens()

        self.console.print("Splitting and re-organizating the code...")

        self.obfuscated.add_line(
            f"{self.splitted}="
            f"{self.eval}({obfuscate_string('str()', _eval=self.eval)})"
        )

        parts = map(
            lambda x: f"{x}\n",
            obfuscated_tokens.splitlines()
        )

        for part in parts:
            key = generate_xor_key()
            encoded = xor_string(part, key)

            obfuscated_key = obfuscate_int(key)

            self.obfuscated.add_line(
                f"{self.splitted}+="
                f"''.join({self.chr}({self.ord}(_)^{obfuscated_key})"
                f"for(_)in({base64_string(encoded)}));",
            )

        code = (
            self.comp
            + "("
            + self.splitted
            + ","
            + obfuscate_string("<string>", range=(1, 2))
            + ","
            + obfuscate_string("exec")
            + ")"
        )

        self.obfuscated.add_line(f"{self.exec}({code})")

    def junk_string(self, length: int = 10, b64: bool = False) -> str:
        """ Generate a random string of a given length """
        string = "".join(random.choice("Il") for _ in range(length))

        if string in self.generated_strings:
            string = self.junk_string(length, b64)

        self.generated_strings.append(string)

        return (
            base64.b64encode(string.encode()).decode().replace("=", "")
            if base64 else string
        )

    def finalize(self) -> str:
        """ Finalize the code """

        self.console.print("Finalizing with zlib compression...")

        compressed = zlib.compress(self.obfuscated.content.encode())

        final = (
            "import sys\n"
            "sys.setrecursionlimit(999999999)\n"
            "exec("
            f"__import__('{string_to_hex('zlib')}').decompress({compressed})"
            ")  # hello from dwoppah"
        )

        final_size = len(final)

        self.console.print(
            f"Final code size: {final_size:,} "
            "(This is very variable, restart the program to get another size)"
        )

        return final
