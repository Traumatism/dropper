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
    """ This is a function """
    print("function called!")
    return a + x


print(1)
print("this is a string")
print(b"this is bytes")
print("this is a float", 0.001)
print("this is a bool", True)
print("this is a 2nd bool", False)
print("this is a function call", function(2, 3))
