import logging
import math
import random

import discord
from discord.ext import commands

from db import Database

logger = logging.getLogger("levels")


def xp_to_level(xp: int) -> int:
    # Simple quadratic curve: level n at xp = 50 * n^2
    return int(math.sqrt(xp / 50))


class LevelsCog(commands.Cog):
    """XP and Level system stored in SQLite via aiosqlite."""

    def __init__(self, bot: commands.Bot, db: Database) -> None:
        self.bot = bot
        self.db = db

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bot messages and DMs
        if message.author.bot or message.guild is None:
            return

        xp_gain = random.randint(5, 10)
        xp, current_level = await self.db.add_message(message.author.id, message.guild.id, xp_gain)
        new_level = xp_to_level(xp)
        if new_level > current_level:
            await self.db.set_level(message.author.id, message.guild.id, new_level)
            try:
                await message.channel.send(f"🎉 {message.author.mention} leveled up to level {new_level}!")
            except Exception:
                logger.exception("Failed to send level up message")

    @commands.command(name="rank", help="Show your level and XP. Usage: !rank [@user]")
    async def rank(self, ctx: commands.Context, member: discord.Member | None = None):
        member = member or ctx.author
        stats = await self.db.get_stats(member.id, ctx.guild.id)
        if not stats:
            await ctx.reply("No stats yet for this user.")
            return
        xp, level, messages, last_active = stats
        await ctx.reply(f"📈 {member.mention} | Level: {level} | XP: {xp} | Messages: {messages}")
