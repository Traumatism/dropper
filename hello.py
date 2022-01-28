def main(string: str, i: int, boolean: bool = False) -> None:
    for _ in range(i):
        print("%s: %s" % (string, boolean))


if __name__ == "__main__":
    main("Hello World!", 3, True)
