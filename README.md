# Discord Trash Bot

## Features
- Startup and configuration
  - Runs with token and configurable command prefix via environment variables
  - Logs status on startup and prints an invite link
  - Centralized structured logging
- Moderation
  - `!kick`, `!ban`, `!clear` with permission checks and chat feedback
- Levels and Experience
  - Earn XP on messages; level-up announcements
  - Data persisted in SQLite (async via aiosqlite)
- Analytics
  - Tracks message counts and last activity
  - `!stats` to show user stats
- Fun/Interactive
  - `!guess <1..10>` mini-game
  - `!advice [topic]` contextual advice
- Code quality
  - Async architecture, docstrings for complex parts, minimal duplication

## Getting Started

### Requirements
- Python 3.11+
- Dependencies in `requirements.txt`

### Environment Variables
Create a `.env` file based on `.env.example`:

```
DISCORD_TOKEN=your_bot_token_here
DISCORD_PREFIX=!
DISCORD_CLIENT_ID=your_application_client_id
DATABASE_PATH=bot.db
```

### Run Locally
```
pip install -r requirements.txt
python main.py
```
On startup, the console prints an "Invite link" you can open to add the bot to a server.

### Docker Compose
The stack includes a dedicated PostgreSQL database container. By default, the bot connects using DATABASE_URL from docker-compose.

To start both services:
```bash
  docker-compose up --build
```
Make sure `.env` is present in the project root. You can override DATABASE_URL in your `.env` if needed.

If you prefer SQLite for local dev, leave DATABASE_URL unset and set DATABASE_PATH (defaults to bot.db); in Docker Compose we use PostgreSQL by default.

## Commands
- Moderation
  - `!kick @member [reason]`
  - `!ban @member [reason]`
  - `!clear <amount>`
- Levels & Analytics
  - `!rank [@user]`
  - `!stats [@user]`
- Fun
  - `!guess <1..10>`
  - `!advice [topic]`

## Custom Decorators
- `command_logger()` — logs each command invocation
- `timing()` — measures execution time
- `require_guild_permissions(**perms)` — ensures the invoker has the required permissions

The `kick` command demonstrates stacking three decorators simultaneously.

## Deployment (Railway example)
1. Create a new Railway project and connect this GitHub repository.
2. Add environment variables: `DISCORD_TOKEN`, `DISCORD_PREFIX`, `DISCORD_CLIENT_ID`, `DATABASE_PATH` (optional).
3. Set Start Command to `python main.py`.
4. Deploy. Logs will show "Bot is online!" and the invite link.

## Invite Link
The bot prints the invite link on startup if `DISCORD_CLIENT_ID` is provided. Format:
```
https://discord.com/api/oauth2/authorize?client_id=<CLIENT_ID>&permissions=8&scope=bot%20applications.commands
```

## Notes
- The bot requires the following Gateway Intents enabled in the Developer Portal: Server Members, Message Content.
- Ensure the bot role has sufficient permissions for moderation commands.
