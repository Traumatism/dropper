def main(string: str, i: int, boolean: bool = False) -> None:
    """Main function"""
    for _ in range(i):
        # dropper test
        print("%s: %s" % (string, boolean))

    a = [1, 2, 3, "4", "5", "6", True]
    eval('print(a)')


if __name__ == "__main__":
    main("Hello World!", 3, True)
