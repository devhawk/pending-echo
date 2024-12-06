import asyncio
from typing import Any, Callable, Coroutine, TypeVar, Generic

T = TypeVar("T")
R = TypeVar("R")


class Immediate(Generic[T]):
    __slots__ = ("_func")

    def __init__(self, func: Callable[[], T]):
        self._func = func

    def then[R](self, func: Callable[[T], R]) -> "Immediate[R]":
        raise NotImplementedError()

    def __call__(self) -> T:
        return self._func()


class Pending(Generic[T]):
    __slots__ = ("_func")

    def __init__(self, func: Callable[[], Coroutine[Any, Any, T]]):
        self._func = func

    def then[R](self, func: Callable[[T], R]) -> "Pending[R]":
        raise NotImplementedError()

    async def __call__(self) -> T:
        return await self._func()


def get_answer():
    return "42"


async def get_question():
    await asyncio.sleep(1)
    return "What is 6 * 9?"
