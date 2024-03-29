import secrets
import random

# https://github.com/therealOri
# https://github.com/Traumatism/Dropper/pull/5
system = secrets.SystemRandom()


def obfuscate_float(value: float) -> str:
    """Obfuscate a float value"""
    unit, sec = map(int, str(value).split("."))
    return f"(({obfuscate_int(unit)})+.{sec})"


def obfuscate_int(value: int, shift: int = system.randint(1, 10)) -> str:
    """Obfuscate an integer value"""

    match random.randint(1, 3):
        case 1:
            return f"{hex(value << shift)}>>{hex(shift)}"
        case 2:
            return f"{bin(value)}"
        case 3:
            return f"{hex(value)}"

    raise


def obfuscate_boolean(value: bool, bool_func: str = "bool") -> str:
    """Obfuscate a boolean value"""
    zero, one = obfuscate_int(0), obfuscate_int(1)
    return f"{bool_func}({zero if value else one})"


def obfuscate_string(value: str, chr_func: str = "chr") -> str:
    """Obfuscate a string value"""
    value = "+".join(f"{chr_func}({obfuscate_int(ord(char))})" for char in value)
    return f"({value})"
