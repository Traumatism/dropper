import os  # this is a module


class Foo:
    """ This is a class """

    def __init__(self) -> None:
        self.__bar = "hello world"

    @classmethod
    def get_foo(cls) -> "Foo":
        return cls()

    def noonewillusethis(self):
        os.system("echo 'hello world'")

    @property
    def bar(self) -> str:
        return self.__bar


def function(a: int, x: int) -> int:
    return function(a - 1, x**2) if a > 0 else x


print("this is a string")
print(b"this is bytes")
