import tokenize
import token
import typing
import random
import zlib
import io

from dropper.methods import obfuscate_int, obfuscate_string, obfuscate_boolean
from dropper.utils import string_to_hex


class Dropper:

    def __init__(self, code: str) -> None:
        self.code = code

        self.io = lambda code: io.BytesIO(code.encode("utf-8"))

        self.tokenize = lambda io: list(tokenize.tokenize(
            io.readline
        ))

        self.junk_strs, self.funcs_map = [], {}

    def junk_string(self) -> str:
        """ Generate a random string """
        s = "".join(random.choice("Ii") for _ in range(15))

        while s and s in self.junk_strs:
            s = "".join(random.choice("Ii") for _ in range(15))

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

                    change_obj_name = not (
                        _token.string.startswith("__")
                        and _token.string.endswith("__")
                    )

                    if change_obj_name:
                        new_obj_name = self.junk_string()
                        self.funcs_map[_token.string] = new_obj_name

                    obj_name = (
                        new_obj_name  # type: ignore
                        if change_obj_name else _token.string
                    )

                    _type, string, start, end, line = (
                        _token.type, obj_name,
                        _token.start, _token.end, _token.line
                    )

            if _type == token.NUMBER:
                value = eval(string)  # i am not in danger, i am the danger.
                string = obfuscate_int(value)

            yield tokenize.TokenInfo(
                type=_type,
                string=string,
                start=start,
                end=end,
                line=line
            )

    def obfuscate(self) -> str:
        """ Obfuscate the code """
        self.code = tokenize.untokenize(
            self.obfuscate_tokens()
        ).decode()

        tokens = self.tokenize(self.io(self.code))
        tokens_iterator = iter(tokens)
        final_tokens = []

        for _token in tokens_iterator:
            _type, string, start, end, line = _token

            if _type == token.NAME:
                if string in self.funcs_map:
                    string = self.funcs_map[string]

            final_tokens.append(
                tokenize.TokenInfo(
                    type=_type,
                    string=string,
                    start=start,
                    end=end,
                    line=line
                )
            )

        obfuscated = tokenize.untokenize(final_tokens)
        compressed = zlib.compress(obfuscated, 9)

        self.code = ""
        self.code += f"""
_ = (
    (e:=eval),
    '{string_to_hex('compile')}',
    e('{string_to_hex('__import__')}'),
    '{string_to_hex('zlib')}'
)

_[{obfuscate_int(0)}](_[{obfuscate_int(0)}](_[{obfuscate_int(1)}])(
    _[{obfuscate_int(2)}](_[{obfuscate_int(3)}])
    .decompress({compressed})
    .decode(),
    '{string_to_hex('<string>')}', '{string_to_hex('exec')}'
))

"""
        return self.code
