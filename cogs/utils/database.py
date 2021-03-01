import asyncio

import asyncpg


class Database(object):
    def __init__(self, bot, pool, loop=None, timeout: float = 60.0):
        self.bot = bot
        self._pool = pool
        self._loop = loop or asyncio
        self.timeout = timeout
        self._rate_limit = asyncio.Semaphore(value=self._pool._maxsize, loop=self._loop)

    @classmethod
    async def create_pool(cls, bot, uri=None, *, min_connections=10, max_connections=10,
                          timeout=60.0, loop=None, **kwargs):
        pool = await asyncpg.create_pool(uri, min_size=min_connections, max_size=max_connections, **kwargs)
        self = cls(bot=bot, pool=pool, loop=loop, timeout=timeout)
        print('Established db pool with {} - {} connections'.format(min_connections, max_connections))
        return self

    async def fetch(self, query, *args):
        async with self._rate_limit:
            async with self._pool.acquire() as con:
                return await con.fetch(query, *args, timeout=self.timeout)

    async def fetchrow(self, query, *args):
        async with self._rate_limit:
            async with self._pool.acquire() as con:
                return await con.fetchrow(query, *args, timeout=self.timeout)

    async def execute(self, query: str, *args):
        async with self._rate_limit:
            async with self._pool.acquire() as con:
                return await con.execute(query, *args, timeout=self.timeout)

    async def get_data(self):
        query = "SELECT * FROM time_data"
        return await self.fetch(query)

    async def add_reminder(self, *args):
        query = "INSERT INTO time_data (day, time, subject, attendees, permanant) VALUES ($1, $2, $3, $4, $5)"
        await self.execute(query, *args)

    async def delete(self, record):
        query = "DELETE FROM time_data WHERE day=$1 AND time=$2"
        await self.execute(query, record['day'], record['time'])

    async def get_test_data(self):
        return await self.fetch("SELECT * FROM test_data")

    async def remove_test(self, record):
        return await self.execute("DELETE FROM test_data WHERE pid=$1", record['pid'])
