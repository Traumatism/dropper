import hashlib
import secrets
import zlib
import time

from io import BytesIO

from typing import Dict, List, Generator

from token import NAME, STRING, NUMBER
from tokenize import untokenize, TokenInfo

from rich.panel import Panel
from rich.table import Table
from rich.console import Console

from ._methods import (
    obfuscate_int,
    obfuscate_float,
    obfuscate_string,
    obfuscate_boolean
)

from ._utils import string_to_hex, io_to_tokens

console = Console()


class Dropper:
    """ Dropper core """

    def __init__(
        self,
        code: str,
        junk_strings_lenght: int = 16,
        obfuscate_bools: bool = True,
        obfuscate_ints: bool = True,
        obfuscate_strings: bool = True,
        obfuscate_names: bool = True,
    ) -> None:

        self.junk_strings_lenght = junk_strings_lenght

        self.code = code

        self.obfuscate_bools = obfuscate_bools
        self.obfuscate_ints = obfuscate_ints
        self.obfuscate_strings = obfuscate_strings
        self.obfuscate_names = obfuscate_names

        self.console = console

        self.junk_strs: List[int] = []
        self.funcs_map: Dict[str, str] = {}

        self._eval = self.junk_string()
        self._bool = self.junk_string()
        self._bytes = self.junk_string()
        self._chr = self.junk_string()
        self._map = self.junk_string()
        self._lbd = self.junk_string()

        table = Table(title="Built-ins")

        table.add_column("Name", justify="left")
        table.add_column("New name", justify="left")
        table.add_column("Description", justify="left")

        table.add_row(
            "chr(...)", f"{self._chr}(...)",
            "Translate a character to its ASCII code"
        )

        table.add_row(
            "eval(...)", f"{self._eval}(...)", "Evaluate a Python expression"
        )
        table.add_row(
            "bool(...)", f"{self._bool}(...)", "Convert a value to a boolean"
        )

        table.add_row(
            "bytes(...)", f"{self._bytes}(...)",
            "Convert a string to a bytes object"
        )

        self.console.log(Panel.fit(table))

    def junk_string(self) -> str:
        """ Generate a random string """

        # https://github.com/therealOri
        # https://github.com/Traumatism/Dropper/pull/5
        s = secrets.randbits(self.junk_strings_lenght)

        if s in self.junk_strs:
            return self.junk_string()

        self.junk_strs.append(s)

        return f"_{hex(s)}"

    def obfuscate_tokens(self) -> Generator[TokenInfo, None, None]:
        """ Tokenize & obfuscate code """
        iterator = io_to_tokens(BytesIO(self.code.encode()), True)

        for token in iterator:
            _type, string, start, end, line = token

            if (
                _type == STRING
                and self.obfuscate_strings
                and string.startswith(("'", "\""))
            ):
                string = obfuscate_string(string[1:-1], self._chr)

            if _type == NAME:

                if string in ("True", "False") and self.obfuscate_bools:
                    string = obfuscate_boolean(eval(string), self._bool)

                if string in ("def", "class") and self.obfuscate_names:
                    yield token

                    token = next(iterator)

                    change_callable_name = not (
                        token.string.startswith("__")
                        and token.string.endswith("__")
                    )

                    name = token.string

                    if change_callable_name:
                        self.funcs_map[token.string] = (
                            name := self.junk_string()
                        )

                    _type, string, start, end, line = (
                        token.type, name, token.start, token.end, token.line
                    )

            if _type == NUMBER:

                if string.isdigit():
                    string = obfuscate_int(eval(string))

                elif "." in string:
                    string = obfuscate_float(eval(string))

            yield TokenInfo(_type, string, start, end, line)

    def finalize(self, code: bytes) -> str:
        """ Finalize the obfuscation """
        _i = map(lambda k: f"({obfuscate_int(k ^ 10)})", list(code))

        _l_content = map(str, (
            self._eval,
            obfuscate_string("compile", self._chr),
            f"{self._eval}({obfuscate_string('__import__', self._chr)})",
            obfuscate_string("zlib", self._chr),
            f"{self._map}({self._eval},{list(_i)})",
            obfuscate_string("sys", self._chr),
            obfuscate_string("<string>", self._chr),
            obfuscate_string("exec", self._chr)
        ))

        _m = f"{self._chr},{self._bytes},{self._bool},{self._map}"

        _m_content = (
            f"{self._eval}({obfuscate_string('chr')})",
            f"{self._eval}({obfuscate_string('bytes')})",
            f"{self._eval}({obfuscate_string('bool')})",
            f"{self._eval}({obfuscate_string('map')})"
        )

        # ignore line length
        # pylint: disable=C0301
        # flake8: noqa: C0301
        # pylint: ignore=line-too-long

        tmp = "\n"

        tmp += f"{self._eval}=eval({obfuscate_string('eval')});"
        tmp += f"{_m}=({','.join(_m_content)});{(_l:=self.junk_string())}=({','.join(_l_content)})"
        tmp += f"""

def {self._lbd}({(a:=self.junk_string())}, {(b:=self.junk_string())}):
    return {self._eval}('{string_to_hex("lambda ")}'+{a}+'{string_to_hex(":")}'+{b})

{(options := self.junk_string())} = {self._lbd}('{(a:=self.junk_string())}','({a}[{obfuscate_int(6)}], {a}[{obfuscate_int(7)}])')
{(decode_f := self.junk_string())} = {self._lbd}('{(a:=self.junk_string())}','{a}^{obfuscate_int(10)}')
{(decode := self.junk_string())} = {self._lbd}('{(a:=self.junk_string())}','{a}[{obfuscate_int(2)}]({a}[{obfuscate_int(3)}]).decompress({self._bytes}({self._map}({decode_f},{self._bytes}({a}[{obfuscate_int(4)}])))).decode()')
{(self.junk_string())} = {self._lbd}('{(a:=self.junk_string())}','({a}[{obfuscate_int(2)}]({a}[{obfuscate_int(5)}]).setrecursionlimit({obfuscate_int(999999999)}))')({_l})
{(self.junk_string())} = {self._lbd}('{(a:=self.junk_string())}','({a}[{obfuscate_int(0)}]({a}[{obfuscate_int(0)}]({a}[{obfuscate_int(1)}])({decode}({a}),*{options}({a}))))')({_l})"""

        md5sum = str(hashlib.md5(tmp.encode()).digest())
        s = secrets.token_hex(64)

        _code = """
# ignore line length
# pylint: disable=C0301
# flake8: noqa: C0301
# pylint: ignore=line-too-long\n"""
        _code += f"(lambda {(r := self.junk_string())}:(eval({obfuscate_string('exit(0)')})if(__import__('{string_to_hex('hashlib')}').md5(open(eval('{string_to_hex('__file__')}')).read().split('{string_to_hex(f'# {s}')}')[{obfuscate_int(1)}].encode()).digest()!={md5sum})else({r})))('{secrets.randbits(64)}')\n# {s}"
        _code += tmp

        return _code

    def __obfuscate(self) -> None:
        """ Obfuscate the code """
        self.console.log(
            "Obfuscating objects... (functions, classes, strings, ints)"
        )

        self.code = obfuscated = untokenize(self.obfuscate_tokens())

        if self.obfuscate_names:
            self.console.log("Changing callable calls names...")

            final_tokens = []

            for token in io_to_tokens(BytesIO(obfuscated), False):
                string, _type = token.string, token.type

                if _type == NAME and (value := self.funcs_map.get(string)):
                    string = value

                final_tokens.append(TokenInfo(
                    _type, string, token.start, token.end, token.line
                ))

            obfuscated = untokenize(final_tokens)

        self.console.log("Compressing code...")

        compressed = zlib.compress(obfuscated, 9)

        self.console.log("Generating final code...")

        self.code = self.finalize(compressed)

        table = Table(title="Functions & classes")

        table.add_column("Name")
        table.add_column("New name")

        for name, new_name in self.funcs_map.items():
            table.add_row(f"{name}(...)", f"{new_name}(...)")

        self.console.log(Panel.fit(table))

    def obfuscate(self) -> str:
        """ Obfuscate the code """

        start = time.perf_counter()
        self.__obfuscate()
        end = time.perf_counter()

        self.console.log(f"Obfuscation done in {end - start:.2f} seconds")

        return self.code
