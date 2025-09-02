import asyncio
import aiosqlite
import asyncpg
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger("db")


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    xp INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 0,
    messages INTEGER NOT NULL DEFAULT 0,
    last_active TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users ON users (user_id, guild_id);
"""

POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    xp INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 0,
    messages INTEGER NOT NULL DEFAULT 0,
    last_active TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users ON users (user_id, guild_id);
"""


class Database:
    """Async DB wrapper supporting SQLite (default) and PostgreSQL (via DATABASE_URL).

    If url is provided and scheme is postgresql, uses asyncpg; otherwise falls back to SQLite.
    """

    def __init__(self, path: str | None = "bot.db", url: str | None = None) -> None:
        self._url = url
        self._path = path or "bot.db"
        self._backend: str = "sqlite"
        self._conn: Optional[aiosqlite.Connection] = None
        self._pool: Optional[asyncpg.Pool] = None

        if url:
            parsed = urlparse(url)
            if parsed.scheme.startswith("postgres"):
                self._backend = "postgres"

    async def init(self) -> None:
        if self._backend == "postgres":
            self._pool = await asyncpg.create_pool(dsn=self._url, min_size=1, max_size=5)
            async with self._pool.acquire() as conn:
                await conn.execute(POSTGRES_SCHEMA)
            logger.info("PostgreSQL initialized at %s", self._url)
        else:
            self._conn = await aiosqlite.connect(self._path)
            await self._conn.executescript(SQLITE_SCHEMA)
            await self._conn.commit()
            logger.info("SQLite initialized at %s", self._path)

    async def close(self) -> None:
        if self._backend == "postgres":
            if self._pool is not None:
                await self._pool.close()
                self._pool = None
                logger.info("PostgreSQL pool closed")
        else:
            if self._conn is not None:
                await self._conn.close()
                self._conn = None
                logger.info("SQLite connection closed")

    # User analytics and XP helpers
    async def add_message(self, user_id: int, guild_id: int, xp_gain: int) -> tuple[int, int]:
        """Increment message count and XP, return (xp, level)."""
        if self._backend == "postgres":
            assert self._pool is not None
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO users (user_id, guild_id, xp, level, messages, last_active)
                    VALUES ($1, $2, 0, 0, 0, NOW())
                    ON CONFLICT (user_id, guild_id) DO NOTHING
                    """,
                    user_id, guild_id,
                )
                await conn.execute(
                    """
                    UPDATE users
                    SET messages = messages + 1,
                        xp = xp + $1,
                        last_active = NOW()
                    WHERE user_id = $2 AND guild_id = $3
                    """,
                    xp_gain, user_id, guild_id,
                )
                row = await conn.fetchrow(
                    "SELECT xp, level FROM users WHERE user_id = $1 AND guild_id = $2",
                    user_id, guild_id,
                )
                return int(row[0]), int(row[1])
        else:
            assert self._conn is not None
            await self._conn.execute(
                """
                INSERT INTO users (user_id, guild_id, xp, level, messages, last_active)
                VALUES (?, ?, 0, 0, 0, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, guild_id) DO NOTHING
                """,
                (user_id, guild_id),
            )
            await self._conn.execute(
                """
                UPDATE users
                SET messages = messages + 1,
                    xp = xp + ?,
                    last_active = CURRENT_TIMESTAMP
                WHERE user_id = ? AND guild_id = ?
                """,
                (xp_gain, user_id, guild_id),
            )
            await self._conn.commit()
            async with self._conn.execute(
                "SELECT xp, level FROM users WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            ) as cur:
                row = await cur.fetchone()
                return int(row[0]), int(row[1])

    async def set_level(self, user_id: int, guild_id: int, level: int) -> None:
        if self._backend == "postgres":
            assert self._pool is not None
            async with self._pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET level = $1 WHERE user_id = $2 AND guild_id = $3",
                    level, user_id, guild_id,
                )
        else:
            assert self._conn is not None
            await self._conn.execute(
                "UPDATE users SET level = ? WHERE user_id = ? AND guild_id = ?",
                (level, user_id, guild_id),
            )
            await self._conn.commit()

    async def get_stats(self, user_id: int, guild_id: int) -> Optional[tuple[int, int, int, str]]:
        if self._backend == "postgres":
            assert self._pool is not None
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT xp, level, messages, COALESCE(to_char(last_active, 'YYYY-MM-DD HH24:MI:SSTZ'), '') FROM users WHERE user_id = $1 AND guild_id = $2",
                    user_id, guild_id,
                )
                if row:
                    return int(row[0]), int(row[1]), int(row[2]), str(row[3])
                return None
        else:
            assert self._conn is not None
            async with self._conn.execute(
                "SELECT xp, level, messages, COALESCE(last_active, '') FROM users WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            ) as cur:
                row = await cur.fetchone()
                if row:
                    return int(row[0]), int(row[1]), int(row[2]), str(row[3])
                return None
