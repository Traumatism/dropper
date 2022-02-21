
import random
import base64
import tokenize

from typing import Union


def edit_token(token: tokenize.TokenInfo, string: str) -> tokenize.TokenInfo:
    """ Edit a token """
    return tokenize.TokenInfo(
        token.type, string, token.start, token.end, token.line
    )


def xor_string(string: str, key: int) -> str:
    """ XOR a string with a key """
    return "".join(chr(ord(char) ^ key) for char in string)


def base64_string(string: str, _eval: str = "eval") -> str:
    """ Convert a string to base64 """
    encoded = base64.b64encode(string.encode()).decode()

    return (
        f"{_eval}(\"{string_to_hex('base64.b64decode')}\")"
        f"(b\"{string_to_hex(encoded)}\").decode()"
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


def obfuscate_string(string: str, _eval: str = "eval") -> str:
    """ Obfuscate a string """
    return "".join(
        f"{_eval}(\"{string_to_hex('chr')}\")({obf_chr})+"
        for obf_chr in (obfuscate_int(ord(char)) for char in string)
    )[:-1]


def obfuscate_int(num: int, shift=random.randint(1, 20)) -> str:
    """ Obfuscate an integer """
    return f"{num << shift}>>{shift}"
