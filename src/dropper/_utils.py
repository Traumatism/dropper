from io import BytesIO
from tokenize import tokenize, TokenInfo
from typing import List, Iterator, Literal, Union, overload


def string_to_hex(value: str) -> str:
    """ Convert a string to hex """
    return "\\x" + "\\x".join(f"{ord(char):02x}" for char in value)


@overload
def io_to_tokens(io, _iter: Literal[True]) -> Iterator[TokenInfo]: ...


@overload
def io_to_tokens(io, _iter: Literal[False]) -> List[TokenInfo]: ...


def io_to_tokens(
    io: BytesIO,
    _iter: Union[Literal[True], Literal[False]] = False
) -> Union[Iterator[TokenInfo], List[TokenInfo]]:
    """ Convert io to tokens """
    r = tokenize(io.readline)
    return iter(r) if _iter else list(r)
