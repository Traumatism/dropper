import tokenize
import token
import typing
import random
import zlib
import io

from rich.panel import Panel
from rich.table import Table  # type: ignore
from rich.console import Console

from dropper.methods import (
    obfuscate_bytes,
    obfuscate_int,
    obfuscate_string,
    obfuscate_boolean
)

from dropper.utils import string_to_hex


class Dropper:

    def __init__(
        self,
        code: str,
        verbose: bool = False,
        junk_strings_lenght: int = 16,
        obfuscate_bools: bool = True,
        obfuscate_ints: bool = True,
        obfuscate_strings: bool = True,
        obfuscate_names: bool = True,
        console: typing.Optional[Console] = None
    ) -> None:

        self.junk_strings_lenght = junk_strings_lenght

        self.code = code
        self.verbose = verbose
        self.obfuscate_bools = obfuscate_bools
        self.obfuscate_ints = obfuscate_ints
        self.obfuscate_strings = obfuscate_strings
        self.obfuscate_names = obfuscate_names

        self.console = console or Console()

        self.io = lambda code: io.BytesIO(code.encode("utf-8"))

        self.tokenize = lambda io: list(tokenize.tokenize(
            io.readline
        ))

        self.junk_strs, self.funcs_map = [], {}

        self._eval = self.junk_string()
        self._bool = self.junk_string()
        self._bytes = self.junk_string()
        self._chr = self.junk_string()

        if self.verbose:
            table = Table(title="Built-ins")
            table.add_column("Name", justify="left")
            table.add_column("New name", justify="left")
            table.add_column("Description", justify="left")

            table.add_row(
                "chr(...)", f"{self._chr}(...)",
                "Translate a character to its ASCII code"
            )

            table.add_row(
                "eval(...)", f"{self._eval}(...)",
                "Evaluate a Python expression"
            )
            table.add_row(
                "bool(...)", f"{self._bool}(...)",
                "Convert a value to a boolean"
            )

            table.add_row(
                "bytes(...)", f"{self._bytes}(...)",
                "Convert a string to a bytes object"
            )

            self.console.log(Panel.fit(table))

    def junk_string(self) -> str:
        """ Generate a random string """

        s = f"_{hex(random.getrandbits(self.junk_strings_lenght))}"

        while not s and s in self.junk_strs:
            s = f"_{hex(random.getrandbits(self.junk_strings_lenght))}"

        self.junk_strs.append(s)

        if self.verbose:
            self.console.log(
                f"Generated a new random string: {s}"
            )

        return s

    def obfuscate_tokens(
        self
    ) -> typing.Generator[tokenize.TokenInfo, None, None]:
        """ Tokenize & obfuscate code """
        tokens = self.tokenize(self.io(self.code))
        tokens_iterator = iter(tokens)

        for _token in tokens_iterator:
            _type, string, start, end, line = _token

            if _type == token.STRING and self.obfuscate_strings:

                if string.startswith(("'", "\"")):
                    """ Normal string """
                    string = obfuscate_string(string[1:-1], self._chr)

                elif string.startswith(("r'", "r\"")):
                    """ Raw strings """
                    string = obfuscate_string(
                        string
                        .replace("\\", "\\\\")
                        .replace("'", "\\'")
                        .replace('"', '\\"')
                        [2:-1],
                        self._chr
                    )

            if _type == token.NAME:

                if string in ("True", "False") and self.obfuscate_bools:
                    string = obfuscate_boolean(
                        eval(string), self._bool
                    )

                if string in ("def", "class") and self.obfuscate_names:
                    yield _token

                    _token = next(tokens_iterator)

                    change_callable_name = not (
                        _token.string.startswith("__")
                        and _token.string.endswith("__")
                    )

                    if change_callable_name:
                        new_callable_name = self.junk_string()
                        self.funcs_map[_token.string] = new_callable_name

                    callable_name = (
                        new_callable_name  # type: ignore
                        if change_callable_name else _token.string
                    )

                    _type, string, start, end, line = (
                        _token.type, callable_name,
                        _token.start, _token.end, _token.line
                    )

            if _type == token.NUMBER:
                value = eval(string)  # i am not in danger, i am the danger.
                string = obfuscate_int(value)

            yield tokenize.TokenInfo(_type, string, start, end, line)

    def obfuscate(self) -> str:
        """ Obfuscate the code """
        self.console.log(
            "Obfuscating objects... (functions, classes, strings, ints)"
        )

        self.code = obfuscated = tokenize.untokenize(
            self.obfuscate_tokens()
        ).decode()

        if self.obfuscate_names:
            self.console.log("Changing callable calls names...")

            tokens = self.tokenize(self.io(self.code))
            tokens_iterator = iter(tokens)
            final_tokens = []

            for _token in tokens_iterator:
                _type, string, start, end, line = _token

                if _type == token.NAME and string in self.funcs_map:
                    string = self.funcs_map[string]

                final_tokens.append(
                    tokenize.TokenInfo(_type, string, start, end, line)
                )

            obfuscated = tokenize.untokenize(final_tokens)

        self.console.log("Compressing code...")

        compressed = zlib.compress(obfuscated, 9)

        self.console.log("Generating final code...")

        _l = self.junk_string()

        self.code = ""
        self.code += f"""
{self._eval},{self._chr},{self._bytes},{self._bool} = (
    eval({obfuscate_string('eval')}),
    eval({obfuscate_string('chr')}),
    eval({obfuscate_string('bytes')}),
    eval({obfuscate_string('bool')})
)

{_l} = (
    {self._eval},
    {obfuscate_string('compile', chr_func=self._chr)},
    {self._eval}({obfuscate_string('__import__', chr_func=self._chr)}),
    {obfuscate_string('zlib', chr_func=self._chr)},
    {obfuscate_bytes(compressed, bytes_func=self._bytes)},
)

{(options := self.junk_string())}=lambda {(s:=self.junk_string())}:(
    '{string_to_hex('<string>')}', '{string_to_hex('exec')}', {s}
)

{(decode := self.junk_string())}=lambda {(data:=self.junk_string())}:(
    {_l}[{obfuscate_int(2)}]({_l}[{obfuscate_int(3)}]).decompress({data}).decode()
)


(lambda {(r:=self.junk_string())}:(
    {_l}[{obfuscate_int(0)}]({_l}[{obfuscate_int(0)}]({_l}[{obfuscate_int(1)}])(
        {decode}({_l}[({obfuscate_int(4)})or({r})]),
        *{options}({options})[:{obfuscate_int(-1)}]
    ))
))({_l})

"""

        if self.verbose:
            table = Table(title="Functions & classes")

            table.add_column("Name")
            table.add_column("New name")

            for name, new_name in self.funcs_map.items():
                table.add_row(f"{name}(...)", f"{new_name}(...)")

            self.console.log(Panel.fit(table))

        self.console.log("Done!")

        return self.code
