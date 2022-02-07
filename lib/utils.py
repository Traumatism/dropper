import random
import base64
import tokenize

from typing import Union


def edit_token(token: tokenize.TokenInfo, string: str) -> tokenize.TokenInfo:
    """ Edit a token """
    return tokenize.TokenInfo(
        type=token.type,
        string=string,
        start=token.start,
        end=token.end,
        line=token.line,
    )


def xor_string(string: str, key: int) -> str:
    """ XOR a string with a key """
    return "".join(chr(ord(char) ^ key) for char in string)


def base64_string(string: str, _import: str = "__import__") -> str:
    """ Convert a string to base64 """
    encoded = base64.b64encode(string.encode()).decode()

    return (
        f"{_import}('{string_to_hex('base64')}')"
        f".b64decode(b'{string_to_hex(encoded)}')"
        ".decode()"
    )


def obfuscate_bool(target: bool, _bool: str = "bool") -> str:
    """ Obfuscate a boolean """
    return f"{_bool}({obfuscate_int(1 if target else 0)})"


def random_bit(as_bool: bool = False) -> Union[int, bool]:
    """ Generate a random bit """
    return bool(random.randint(0, 1)) if as_bool else random.randint(0, 1)


def string_to_hex(string: str) -> str:
    """ Convert a string to hex """
    return "\\x" + "\\x".join(f"{hex(ord(char))[2:]}" for char in string)


def int_to_hex_or_bin(num: int) -> str:
    """ Convert an integer to hex or binary """
    return hex(num) if random_bit() else bin(num)


def obfuscate_string(string: str, range=(10, 15), _eval: str = "eval") -> str:
    """ Obfuscate a string """

    array = (obfuscate_int(ord(char), range=range) for char in string)
    quote = random.choice(("'", '"'))

    obfuscated = "".join(
        f"{_eval}({quote}{string_to_hex('chr')}{quote})({obf_chr})+"
        for obf_chr in array
    )

    return obfuscated[:-1]  # Remove the last '+'


def obfuscate_int(num: int, range=(1, 20)) -> str:
    """ Obfuscate an integer """

    shift = random.randint(*range)

    return f"({int_to_hex_or_bin(num << shift)}>>{shift})"
