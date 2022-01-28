import random
import base64


def base64_string(string: str) -> str:
    """Convert a string to base64"""
    encoded = base64.b64encode(string.encode()).decode()

    return (
        f"__import__('{string_to_hex('base64')}')"
        f".b64decode(b'{string_to_hex(encoded)}')"
        ".decode()"
    )


def obfuscate_bool(bool_: bool) -> str:
    """Obfuscate a boolean"""
    return f"bool({obfuscate_int(1 if bool_ else 0)})"


def random_bit(as_bool: bool = False) -> int | bool:
    """Generate a random bit"""
    return bool(random.randint(0, 1)) if as_bool else random.randint(0, 1)


def docstring(text: str, quote: str = '"') -> str:
    """Generate a docstring"""
    return f"{quote*3} {text} {quote*3}"


def string_to_hex(string: str) -> str:
    """Convert a string to hex"""
    return "\\x" + "\\x".join(f"{hex(ord(char))[2:]}" for char in string)


def int_to_hex_or_bin(num: int) -> str:
    """Convert an integer to hex or binary"""
    return hex(num) if random_bit() else bin(num)


def int_to_list_of_bits(num: int):
    """Convert an integer to a list of bits"""
    return list(map(int, int_to_list_of_bool(num)))


def int_to_list_of_bool(num: int) -> list[bool]:
    """Convert an integer to a list boolean"""
    if num >= 15:
        raise ValueError("Integer too large, must be <= 15")

    results = []

    while results.count(True) != num:
        results.append(bool(random_bit()))

    return results


def obfuscate_string(string: str, range=(25, 50)) -> str:
    """Obfuscate a string"""

    array = (obfuscate_int(ord(char), range=range) for char in string)
    quote = random.choice(("'", '"'))

    obfuscated = "".join(
        f"eval({quote}{string_to_hex('chr')}{quote})" f"({obf_chr})" "+"
        for obf_chr in array
    )

    return obfuscated[:-1]  # Remove the last '+'


def obfuscate_int(num: int, range=(50, 100)) -> str:
    """Obfuscate an integer"""

    shift, shift_zero = random.randint(*range), random.randint(*range)
    bit = random_bit()

    parts = (
        f"({int_to_hex_or_bin(num << shift)}>>{shift})",
        f"({int_to_hex_or_bin(1 >> shift_zero)}<<{shift_zero})",
    )

    return parts[bit] + "+" + parts[not bit]
