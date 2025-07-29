import inspect
from typing import Callable


def is_valid_callback(fun: Callable, required_args: list[str]) -> bool:
    """Checks if the given function is a coroutine and has the arguments listed in required_args as keyword arguments."""
    if not inspect.iscoroutinefunction(fun):
        return False
    params = inspect.signature(fun).parameters
    kwargs = {p.name for p in params.values() if p.kind == inspect.Parameter.KEYWORD_ONLY or p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD}
    has_var_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
    return has_var_kwargs or all(arg in kwargs for arg in required_args)