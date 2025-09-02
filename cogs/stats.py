import logging

import discord
from discord.ext import commands

from db import Database
from decorators import command_logger, timing

logger = logging.getLogger("stats")


class StatsCog(commands.Cog):
    """User analytics and statistics commands."""

    def __init__(self, bot: commands.Bot, db: Database) -> None:
        self.bot = bot
        self.db = db

    @commands.command(name="stats", help="Show statistics for a user. Usage: !stats [@user]")
    @command_logger()
    @timing()
    async def stats(self, ctx: commands.Context, member: discord.Member | None = None):
        member = member or ctx.author
        stats = await self.db.get_stats(member.id, ctx.guild.id)
        if not stats:
            await ctx.reply("No stats yet for this user.")
            return
        xp, level, messages, last_active = stats
        embed = discord.Embed(title=f"Stats for {member.display_name}", color=discord.Color.blurple())
        embed.add_field(name="Level", value=str(level))
        embed.add_field(name="XP", value=str(xp))
        embed.add_field(name="Messages", value=str(messages))
        if last_active:
            embed.set_footer(text=f"Last active: {last_active}")
        await ctx.reply(embed=embed)
