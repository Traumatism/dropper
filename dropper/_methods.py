import secrets


# https://github.com/therealOri
# https://github.com/Traumatism/Dropper/pull/5
system = secrets.SystemRandom()


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
    return (
        "(%s)"
        % "+".join(f"{chr_func}({obfuscate_int(ord(char))})" for char in value)
    )


def obfuscate_bytes(value: bytes, bytes_func: str = "bytes") -> str:
    """ Obfuscate a bytes value """
    final = f"{bytes_func}(["

    for byte in value:
        final += f"{byte},"

    return f'{final[:-1]}])'
