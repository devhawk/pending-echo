import asyncio
import functools
from typing import Any, Callable, Coroutine, TypeVar, Generic

T = TypeVar("T")
R = TypeVar("R")


class Immediate(Generic[T]):
    __slots__ = "_func"

    def __init__(self, func: Callable[[], T]):
        self._func = func

    def then(self, next: Callable[[Callable[[], T]], R]) -> "Immediate[R]":
        return Immediate(lambda: next(self._func))

    def __call__(self) -> T:
        return self._func()


class Pending(Generic[T]):
    __slots__ = "_func"

    def __init__(self, func: Callable[[], Coroutine[Any, Any, T]]):
        self._func = func

    @staticmethod
    def _raise(ex: BaseException):
        raise ex

    @staticmethod
    async def _do(
        func: Callable[[], Coroutine[Any, Any, T]], next: Callable[[Callable[[], T]], R]
    ) -> R:
        try:
            value = await func()
            return next(lambda: value)
        except BaseException as exp:
            return next(lambda: Pending._raise(exp))

    def then(self, next: Callable[[Callable[[], T]], R]) -> "Pending[R]":
        return Pending[R](lambda: Pending._do(self._func, next))

    async def __call__(self) -> T:
        return await self._func()


def get_answer():
    return "42"


async def get_question():
    await asyncio.sleep(0.1)
    return "What is 6 * 9?"


def print_result(func: Callable[[], str]) -> str:
    try:
        result = func()
        print(result)
        return result
    except BaseException as exp:
        print(exp)
        raise


s = Immediate(get_answer).then(print_result)
s()

a = Pending(get_question).then(print_result)
asyncio.run(a())
