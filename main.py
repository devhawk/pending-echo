import asyncio
import contextlib
import functools
from types import TracebackType
from typing import Any, Callable, Coroutine, Optional, Type, TypeVar, Generic

T = TypeVar("T")
R = TypeVar("R")


class Immediate(Generic[T]):
    __slots__ = "_func"

    def __init__(self, func: Callable[[], T]):
        self._func = func

    def then(self, next: Callable[[Callable[[], T]], R]) -> "Immediate[R]":
        return Immediate(lambda: next(self._func))
    
    @staticmethod
    def _also(func: Callable[[], T], cm: contextlib.AbstractContextManager):
        with cm:
            return func()
        
    def also(self, cm: contextlib.AbstractContextManager) -> "Immediate[T]":
        return Immediate[T](lambda: Immediate._also(self._func, cm))

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

    @staticmethod
    async def _also(func: Callable[[], Coroutine[Any, Any, T]], cm: contextlib.AbstractContextManager):
        with cm:
            return await func()

    def also(self, cm: contextlib.AbstractContextManager) -> "Pending[T]":
        return Pending[T](lambda: Pending._also(self._func, cm))

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


class PrintContextManager(contextlib.AbstractContextManager):
    def __init__(self, value: str):
        self._value = value

    def __enter__(self):
        print(f"PrintContextManager.__enter__ {self._value}")
        return super().__enter__()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ):
        print(f"PrintContextManager.__exit__ {self._value}")
        return super().__exit__(exc_type, exc_value, traceback)


s = Immediate(get_answer).then(print_result).also(PrintContextManager("sync"))
s()

a = Pending(get_question).then(print_result).also(PrintContextManager("async"))
asyncio.run(a())
