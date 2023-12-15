import asyncio
from typing import Callable, Awaitable
from functools import wraps


class Test(object):
    def __init__(self, limit1: int, limit2: int) -> None:
        self.limit1 = limit1
        self.limit2 = limit2

    def deco(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            print("Deco without args", func.__name__)
            return func(self, *args, **kwargs)

        return wrapper

    def deco_arg(arg):
        def deco(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                print("Deco with arg", arg, func.__name__)
                return func(self, *args, **kwargs)

            return wrapper

        return deco

    def self_deco(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            print("Self deco args", self.limit1, self.limit2, func.__name__)
            return func(self, *args, **kwargs)

        return wrapper

    @deco
    def func1(self, arg1, arg2):
        print(arg1, arg2, "in func1")
        return "data1"

    @deco
    def func2(self, arg1, arg2):
        print(arg1, arg2, "in func2")
        return "data2"

    @deco_arg(1)
    def func3(self, arg1, arg2):
        print(arg1, arg2, "in func3")
        return "data3"

    @deco_arg(2)
    def func4(self, arg1, arg2):
        print(arg1, arg2, "in func4")
        return "data4"

    @self_deco
    def func5(self, arg1, arg2):
        print(arg1, arg2, "in func5")
        return "data5"

    @self_deco
    def func6(self, arg1, arg2):
        print(arg1, arg2, "in func6")
        return "data6"


def test():
    tester = Test(88, 99)

    data1 = tester.func1(1, 2)
    data2 = tester.func2(3, 4)
    data3 = tester.func3(5, 6)
    data4 = tester.func4(7, 8)
    data5 = tester.func5(9, 10)
    data6 = tester.func6(11, 12)

    print(data1, data2, data3, data4, data5, data6)


class AsyncTest(object):
    def __init__(self, limit1: int, limit2: int) -> None:
        self.limit1 = limit1
        self.limit2 = limit2

    def deco(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            print("Deco without args", func.__name__)
            return await func(self, *args, **kwargs)

        return wrapper

    def deco_arg(arg):
        def deco(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                print("Deco with arg", arg, func.__name__)
                return await func(self, *args, **kwargs)

            return wrapper

        return deco

    def self_deco(func: Awaitable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> Awaitable:
            print("Self deco args", self.limit1, self.limit2, func.__name__)
            return await func(self, *args, **kwargs)

        return wrapper

    @deco
    async def func1(self, arg1, arg2):
        print(arg1, arg2, "in func1")
        return "data1"

    @deco
    async def func2(self, arg1, arg2):
        print(arg1, arg2, "in func2")
        return "data2"

    @deco_arg(1)
    async def func3(self, arg1, arg2):
        print(arg1, arg2, "in func3")
        return "data3"

    @deco_arg(2)
    async def func4(self, arg1, arg2):
        print(arg1, arg2, "in func4")
        return "data4"

    @self_deco
    async def func5(self, arg1, arg2):
        print(arg1, arg2, "in func5")
        return "data5"

    @self_deco
    async def func6(self, arg1, arg2):
        print(arg1, arg2, "in func6")
        return "data6"


async def async_test():
    tester = AsyncTest(88, 99)

    data1 = await tester.func1(1, 2)
    data2 = await tester.func2(3, 4)
    data3 = await tester.func3(5, 6)
    data4 = await tester.func4(7, 8)
    data5 = await tester.func5(9, 10)
    data6 = await tester.func6(11, 12)

    print(data1, data2, data3, data4, data5, data6)


if __name__ == "__main__":
    # test()
    asyncio.run(async_test())
