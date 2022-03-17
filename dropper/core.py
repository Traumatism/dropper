import tokenize
import token
import typing
import random
import zlib
import io

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
        self, code: str, console: typing.Optional[Console] = None
    ) -> None:
        self.code = code
        self.console = console or Console()

        self.io = lambda code: io.BytesIO(code.encode("utf-8"))

        self.tokenize = lambda io: list(tokenize.tokenize(
            io.readline
        ))

        self.junk_strs, self.funcs_map = [], {}

    def junk_string(self) -> str:
        """ Generate a random string """
        s = f"_{hex(random.getrandbits(16))}"

        while s and s in self.junk_strs:
            s = f"_{hex(random.getrandbits(16))}"

        self.junk_strs.append(s)

        return s

    def obfuscate_tokens(
        self
    ) -> typing.Generator[tokenize.TokenInfo, None, None]:
        """ Tokenize & obfuscate code """
        tokens = self.tokenize(self.io(self.code))
        tokens_iterator = iter(tokens)

        for _token in tokens_iterator:
            _type, string, start, end, line = _token

            if _type == token.STRING:

                if string.startswith(("'", "\"")):
                    """ Normal string """
                    string = obfuscate_string(string[1:-1])

                elif string.startswith(("r'", "r\"")):
                    """ Raw strings """
                    string = obfuscate_string(
                        string
                        .replace("\\", "\\\\")
                        .replace("'", "\\'")
                        .replace('"', '\\"')
                        [2:-1]
                    )

            if _type == token.NAME:

                if string in ("True", "False"):
                    string = obfuscate_boolean(eval(string))

                if string in ("def", "class"):
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

        self.code = tokenize.untokenize(
            self.obfuscate_tokens()
        ).decode()

        self.console.log("Changing callable calls names...")

        tokens = self.tokenize(self.io(self.code))
        tokens_iterator = iter(tokens)
        final_tokens = []

        for _token in tokens_iterator:
            _type, string, start, end, line = _token

            if _type == token.NAME:
                if string in self.funcs_map:
                    string = self.funcs_map[string]

            final_tokens.append(
                tokenize.TokenInfo(_type, string, start, end, line)
            )

        obfuscated = tokenize.untokenize(final_tokens)

        self.console.log("Compressing code...")
        compressed = zlib.compress(obfuscated, 9)

        _eval = self.junk_string()
        _bytes = self.junk_string()
        _chr = self.junk_string()
        _l = self.junk_string()

        self.console.log("Generating final code...")

        self.code = ""

        self.code += f"""
{_eval},{_chr},{_bytes} = (
    eval({obfuscate_string('eval')}),
    eval({obfuscate_string('chr')}),
    eval({obfuscate_string('bytes')})
)

{_l} = (
    {_eval},
    {obfuscate_string('compile', chr_func=_chr)},
    {_eval}({obfuscate_string('__import__', chr_func=_chr)}),
    {obfuscate_string('zlib', chr_func=_chr)},
    {obfuscate_bytes(compressed, bytes_func=_bytes)},
)

del {_eval},{_chr},{_bytes}

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

        self.console.log("Done!")

        return self.code
