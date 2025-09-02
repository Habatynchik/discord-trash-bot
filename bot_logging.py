import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure centralized logging for the bot.

    Format includes time, level, logger name, and message.
    """
    root = logging.getLogger()
    if root.handlers:
        # Avoid duplicate handlers when reloading
        for h in list(root.handlers):
            root.removeHandler(h)

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(handler)

    # Reduce noise from external libs
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("discord.client").setLevel(logging.INFO)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
