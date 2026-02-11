import asyncio

from typing import (
    Any,
    Dict,
    Optional,
    TypeAlias,
    Coroutine,
    Callable,
)


class ErrorBase(Exception):
    default_message: str = "Internal server error"
    default_status_code: int = 500

    def __init__(self, message: Optional[str] = None, status_code: Optional[int] = None) -> None:
        self.message = message or self.default_message
        self.status = status_code or self.default_status_code

    @staticmethod
    def handle(exc: "ErrorBase"):
        print("ebat' menya v sraku:", exc.message)


class AccessError(ErrorBase):
    default_message: str = "Access denied"
    defeault_status_code: int = 403


class AlreadyExistsError(ErrorBase):
    default_message: str = "Resource already exists"
    defeault_status_code: int = 409


class NotFoundError(ErrorBase):
    default_message: str = "Resource not found"
    defeault_status_code: int = 404


Error: TypeAlias = Exception | ErrorBase
ExceptionHandler: TypeAlias = Callable[[Error], Any]
ExceptionHandlers: TypeAlias = Dict[Error, ExceptionHandler]


EXCEPTION_HANDLERS: ExceptionHandlers = {  # type:ignore
    AccessError: AccessError.handle,
}


def handle_exceptions(
    exc_handlers: ExceptionHandlers,
    callable: Callable | Coroutine,
    run_async: bool = False,
    *args, **kwargs
):
    try:
        if run_async is False:
            if not isinstance(callable, Callable):
                raise ValueError("'run_async' is False, but 'callable' is a coroutine object")
            res = callable(*args, **kwargs)
        else:
            if not isinstance(callable, Coroutine):
                raise ValueError("'run_async' is True, but 'callable' is not a coroutine object")
            res = asyncio.run(callable)
        return res
    except Exception as exc:
        for exc_kind, handle in exc_handlers.items():
            if exc.__class__ == exc_kind.__class__:
                handle(exc)
                return
        raise exc


def handle(func):
    def wrap(*args, **kwargs):
        res = handle_exceptions(EXCEPTION_HANDLERS, func, *args, **kwargs)
        return res
    return wrap
