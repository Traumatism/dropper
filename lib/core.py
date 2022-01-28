import zlib
import random
import base64
import tokenize

from .utils import (
    base64_string, string_to_hex,
    random_bit,
    obfuscate_bool,
    obfuscate_int,
    obfuscate_string, xor_string,
)

from rich.console import Console


class Obfuscated:
    """Manage obfuscated code"""

    def __init__(self):
        self.indent_level: int = 0
        self.__content: str = ""

    def add_line(self, line: str, end=" # /!\\ POWAH OF UWU /!\\\n") -> None:
        """Add a line to the code"""
        self.__content += ("    " * self.indent_level) + line + end

    @property
    def content(self) -> str:
        """Return the content"""
        return self.__content


class Obfuscator:
    """Obfuscate a file"""

    def __init__(self, file_name: str):
        self.console = Console()

        self.file = open(file_name, "r")

        with open(file_name, "r") as file:
            if "# hello from dwoppah" in file.read():
                self.console.print("Already obfuscated!")
                exit(0)

        self.generated_strings: list[str] = []

        self.xor_key = random.randint(10000, 99999)

        self.eval = self.junk_string(10)
        self.mainf = self.junk_string(10)
        self.mainc = self.junk_string(10)
        self.exec = self.junk_string(10)
        self.comp = self.junk_string(10)
        self.none = self.junk_string(10)
        self.name = self.junk_string(10)
        self.hash = self.junk_string(10)
        self.arra = self.junk_string(10)

        self.obfuscated = Obfuscated()
        self.ident_level: int = 0

    def obfuscate_tokens(self) -> str:
        self.console.print("Tokenizing code...")

        _tokens = tokenize.generate_tokens(self.file.readline)

        tokens = []

        for token in _tokens:

            if token.type == 62:
                continue

            if token.type == 3:
                key = random.randint(0, 255)

                encoded = xor_string(token.string[1:-1], key)
                obfuscated_key = obfuscate_int(key)

                real = (
                    f"(''.join(chr(ord(char)^{obfuscated_key}) "
                    f"for char in {base64_string(encoded)}))"
                )

                token = tokenize.TokenInfo(
                    type=token.type,
                    string=real,
                    start=token.start,
                    end=token.end,
                    line=token.line,
                )

            if token.type == 2:

                token = tokenize.TokenInfo(
                    type=token.type,
                    string=obfuscate_int(int(token.string), range=(1, 3)),
                    start=token.start,
                    end=token.end,
                    line=token.line,
                )

            if token.type == 1 and token.string in ("False", "True"):

                token = tokenize.TokenInfo(
                    type=token.type,
                    string=obfuscate_bool(eval(token.string)),
                    start=token.start,
                    end=token.end,
                    line=token.line,
                )

            tokens.append(token)

        return tokenize.untokenize(tokens)

    def obfuscate(self):
        """Obfuscate the code"""

        self.console.print("Generating template...")

        self.obfuscated.add_line(
            f"{self.eval}=eval({obfuscate_string('eval')});", end=""
        )

        obfuscated_exec = f"{self.eval}({obfuscate_string('exec')})"

        self.obfuscated.add_line(f"{self.exec}={obfuscated_exec};", end="")
        self.obfuscated.add_line("\n")

        self.obfuscated.add_line(
            f"{self.none},{self.comp}"
            "="
            f"{self.eval}('{string_to_hex('None')}')"
            ","
            f"{self.eval}('{string_to_hex('compile')}')"
        )

        obfuscated_tokens = self.obfuscate_tokens()

        lines = obfuscated_tokens.splitlines()

        self.obfuscated.add_line(
            f"{self.arra}={self.eval}({obfuscate_string('str()')});"
        )

        for line in lines:
            line += "\n"

            if bool(random_bit()):
                self.obfuscated.add_line(
                    f"{self.arra}+={obfuscate_string(line)};"
                )

            else:
                encoded = xor_string(line, self.xor_key)
                obfuscated_key = obfuscate_int(self.xor_key)

                self.obfuscated.add_line(
                    f"{self.arra}+="
                    f"''.join(chr(ord(_)^{obfuscated_key}) "
                    f"for _ in '{encoded}');"
                )

        code = ""
        code += self.comp
        code += "("
        code += self.arra
        code += ","
        code += obfuscate_string("<string>", range=(1, 2))
        code += ","
        code += obfuscate_string("exec")
        code += ")"

        self.obfuscated.add_line(f"{self.exec}({code})")

    def junk_string(self, length: int = 10, b64: bool = False) -> str:
        """Generate a random string of a given length"""
        string = "".join(random.choice("Il") for _ in range(length))

        if string in self.generated_strings:
            string = self.junk_string(length, b64)

        self.generated_strings.append(string)

        return (
            base64.b64encode(string.encode()).decode().replace("=", "")
            if base64 else string
        )

    def finalize(self) -> str:
        """Finalize the code"""

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
