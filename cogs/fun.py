import logging
import random

import discord
from discord.ext import commands

from decorators import command_logger, timing

logger = logging.getLogger("fun")

ADVICE = [
    "Trust your instincts.",
    "Take breaks; clarity comes with rest.",
    "Ask questions—curiosity leads to solutions.",
    "Start small; iterate often.",
]


class FunCog(commands.Cog):
    """Interactive fun/assistant commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="guess", help="Guess a number between 1 and 10. Usage: !guess 7")
    @command_logger()
    @timing()
    async def guess(self, ctx: commands.Context, pick: int):
        if not 1 <= pick <= 10:
            await ctx.reply("Pick a number between 1 and 10.")
            return
        target = random.randint(1, 10)
        if pick == target:
            await ctx.reply(f"🎯 Correct! The number was {target}.")
        else:
            hint = "higher" if pick < target else "lower"
            await ctx.reply(f"❌ Not quite. The number is {hint} than {pick}. It was {target}.")

    @commands.command(name="advice", help="Get a random piece of advice. Usage: !advice [topic]")
    @command_logger()
    @timing()
    async def advice(self, ctx: commands.Context, *, topic: str | None = None):
        if topic:
            msg = random.choice(ADVICE)
            await ctx.reply(f"On {topic}: {msg}")
        else:
            await ctx.reply(random.choice(ADVICE))
