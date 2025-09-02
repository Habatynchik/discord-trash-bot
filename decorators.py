import asyncio
import logging
from functools import wraps
from typing import Callable, Coroutine, Any

from discord.ext import commands

logger = logging.getLogger("decorators")


def command_logger():
    """Decorator to log command invocation before execution.

    Works with both free functions (ctx first) and cog methods (self, ctx, ...).
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = None
            if args:
                if isinstance(args[0], commands.Context):
                    ctx = args[0]
                elif len(args) > 1 and isinstance(args[1], commands.Context):
                    ctx = args[1]
            if ctx is None:
                ctx = kwargs.get("ctx")

            if ctx is not None:
                logger.info(
                    "Command invoked: %s by %s in #%s",
                    func.__name__,
                    getattr(ctx, "author", "unknown"),
                    getattr(getattr(ctx, "channel", None), "name", "DM"),
                )
            else:
                logger.info("Command invoked: %s", func.__name__)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def timing():
    """Decorator to measure command execution time and log it.

    Works with both free functions and cog methods.
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            start = loop.time()
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed = (loop.time() - start) * 1000
                logger.info("Command %s took %.2f ms", func.__name__, elapsed)

        return wrapper

    return decorator


def require_guild_permissions(**perms):
    """Decorator to require guild permissions with a custom error message/log.

    Works with both free functions and cog methods.
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        check = commands.has_guild_permissions(**perms)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find ctx regardless of whether this is a bound method
            ctx = None
            if args:
                if isinstance(args[0], commands.Context):
                    ctx = args[0]
                elif len(args) > 1 and isinstance(args[1], commands.Context):
                    ctx = args[1]
            if ctx is None:
                ctx = kwargs.get("ctx")

            if ctx is None:
                return await func(*args, **kwargs)

            pred = check.predicate
            if not await commands.utils.maybe_coroutine(pred, ctx):
                logger.warning("Permission denied for %s on %s", getattr(ctx, "author", "unknown"), func.__name__)
                raise commands.MissingPermissions(list(perms.keys()))
            return await func(*args, **kwargs)

        return wrapper

    return decorator
