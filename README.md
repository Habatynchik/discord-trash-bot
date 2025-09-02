# Discord Trash Bot

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
DATABASE_URL=database_url_here
```

### Run Locally
```
pip install -r requirements.txt
python main.py
```
On startup, the console prints an "Invite link" you can open to add the bot to a server.

### Docker Compose
The stack includes a dedicated PostgreSQL database container. 
By default, the bot connects using DATABASE_URL from docker-compose.

To start both services:
```bash
  docker-compose up --build
```
Make sure `.env` is present in the project root. You can override DATABASE_URL in your `.env` if needed.

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

The `kick` command demonstrates stacking three decorators simultaneously.

## Invite Link
The bot prints the invite link on startup if `DISCORD_CLIENT_ID` is provided. Format:
```
    https://discord.com/api/oauth2/authorize?client_id=<CLIENT_ID>&permissions=8&scope=bot%20applications.commands
```