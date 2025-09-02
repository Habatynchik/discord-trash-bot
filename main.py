import asyncio
import logging
import os
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot_logging import setup_logging
from db import Database
from cogs.moderation import ModerationCog
from cogs.levels import LevelsCog
from cogs.stats import StatsCog
from cogs.fun import FunCog


def get_env(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Environment variable {name} is required but not set")
    return value


async def main():
    # Load env and configure logging
    load_dotenv()
    setup_logging()
    logger = logging.getLogger("bot")

    token = get_env("DISCORD_TOKEN", required=True)
    prefix = get_env("DISCORD_PREFIX", default="!")
    client_id = get_env("DISCORD_CLIENT_ID")

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.guilds = True
    intents.messages = True

    bot = commands.Bot(command_prefix=prefix, intents=intents)

    # Centralized on_ready logging
    @bot.event
    async def on_ready():
        logger.info("Bot is online as %s (id=%s)", bot.user, bot.user and bot.user.id)
        print("Bot is online!")
        if client_id:
            invite_link = (
                f"https://discord.com/api/oauth2/authorize?client_id={client_id}"
                f"&permissions=8&scope=bot%20applications.commands"
            )
            logger.info("Invite link: %s", invite_link)
            print(f"Invite link: {invite_link}")

    @bot.event
    async def on_command_error(ctx: commands.Context, error: Exception):
        # Provide user-friendly messages for common errors and log everything
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("⛔ You don't have permission to use this command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.reply("❗ Invalid arguments. Use help for usage details.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("❗ Missing arguments. Use help for usage details.")
        else:
            await ctx.reply("⚠️ An error occurred while executing the command.")
        logger.exception("Command error in %s: %s", ctx.command, error)

    # Initialize database and add cogs
    database_url = get_env("DATABASE_URL")
    if database_url:
        db = Database(url=database_url)
    else:
        db = Database(path=get_env("DATABASE_PATH", "bot.db"))
    await db.init()

    await bot.add_cog(ModerationCog(bot))
    await bot.add_cog(LevelsCog(bot, db))
    await bot.add_cog(StatsCog(bot, db))
    await bot.add_cog(FunCog(bot))

    # Graceful shutdown
    async def shutdown():
        logger.info("Shutting down bot...")
        await db.close()

    try:
        logger.info("Starting bot with prefix '%s'", prefix)
        await bot.start(token)
    except Exception:
        logger.exception("Bot crashed with an unexpected error")
    finally:
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
