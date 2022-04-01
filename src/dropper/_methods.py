import secrets
import functools


# https://github.com/therealOri
# https://github.com/Traumatism/Dropper/pull/5
system = secrets.SystemRandom()


@functools.lru_cache()
def prime_factors(value: int) -> str:
    """ Recursively find prime factors """
    return next(
        (
            f"{prime_factors(factor)}*{prime_factors(value // factor)}"
            for factor in range(2, value) if value % factor == 0
        ), str(value),
    )


def obfuscate_float(value: float) -> str:
    """ Obfuscate a float value """
    unit, sec = map(int, str(value).split("."))
    return f"(({obfuscate_int(unit)})+.{sec})"


def obfuscate_int(value: int) -> str:
    """ Obfuscate an integer value """
    shift = system.randint(0, 100)
    return f"{hex(value ^ shift)}^{hex(shift)}"


def obfuscate_boolean(value: bool, bool_func: str = "bool") -> str:
    """ Obfuscate a boolean value """
    zero, one = obfuscate_int(0), obfuscate_int(1)
    return f"{bool_func}({zero if bool(value) else one})"


def obfuscate_string(value: str, chr_func: str = "chr") -> str:
    """ Obfuscate a string value """
    value = "+".join(
        f"{chr_func}({obfuscate_int(ord(char))})" for char in value
    )

    return f"({value})"
