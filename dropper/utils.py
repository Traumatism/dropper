

def string_to_hex(value: str) -> str:
    """ Convert a string to hex """
    return "\\x" + "\\x".join(f"{ord(char):02x}" for char in value)
