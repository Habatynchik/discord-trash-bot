import logging
from typing import Optional

import discord
from discord.ext import commands

from decorators import command_logger, timing, require_guild_permissions

logger = logging.getLogger("moderation")


class ModerationCog(commands.Cog):
    """Moderation commands like kick, ban, and clear."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="kick", help="Kick a member. Usage: !kick @member [reason]")
    @command_logger()
    @timing()
    @require_guild_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
            await ctx.reply("You cannot kick a member with an equal or higher role.")
            return
        try:
            await member.kick(reason=reason)
            await ctx.reply(f"✅ Kicked {member.mention}. Reason: {reason or 'No reason provided.'}")
            logger.info("%s kicked %s: %s", ctx.author, member, reason)
        except discord.Forbidden:
            await ctx.reply("I don't have permission to kick this member.")
        except Exception:
            logger.exception("Error kicking member")
            await ctx.reply("An error occurred while trying to kick the member.")

    @commands.command(name="ban", help="Ban a member. Usage: !ban @member [reason]")
    @command_logger()
    @timing()
    @require_guild_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
            await ctx.reply("You cannot ban a member with an equal or higher role.")
            return
        try:
            await member.ban(reason=reason, delete_message_days=0)
            await ctx.reply(f"✅ Banned {member.mention}. Reason: {reason or 'No reason provided.'}")
            logger.info("%s banned %s: %s", ctx.author, member, reason)
        except discord.Forbidden:
            await ctx.reply("I don't have permission to ban this member.")
        except Exception:
            logger.exception("Error banning member")
            await ctx.reply("An error occurred while trying to ban the member.")

    @commands.command(name="clear", help="Clear N messages in this channel. Usage: !clear 10")
    @command_logger()
    @timing()
    @require_guild_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int):
        if amount <= 0 or amount > 500:
            await ctx.reply("Please specify an amount between 1 and 500.")
            return
        deleted = await ctx.channel.purge(limit=amount + 1)  # include the command message
        await ctx.send(f"🧹 Deleted {max(len(deleted)-1,0)} messages.", delete_after=5)
        logger.info("%s cleared %s messages in #%s", ctx.author, amount, ctx.channel)
