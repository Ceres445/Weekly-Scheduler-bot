import asyncio
import datetime

import discord
from aiohttp import ClientSession
from discord.ext import commands

from cogs.utils.database import Database
from config import postgres, token, guild, log_channel, announcement

cogs = ["cogs.reminder", "cogs.help", 'cogs.misc', 'cogs.management']


class Riser(commands.Bot):
    def __init__(self, **kwargs):
        allowed_mentions = discord.AllowedMentions(everyone=False, roles=True, users=True)
        super().__init__(command_prefix=kwargs.pop('command_prefix', ['+']), case_insensitive=True,
                         allowed_mentions=allowed_mentions)
        self.session = ClientSession(loop=self.loop)
        self.start_time = datetime.datetime.utcnow()
        self.clean_text = commands.clean_content(escape_markdown=True, fix_channel_mentions=True)
        self.guild = None
        self.db, self.log_channel = None, None
        self.announcement = announcement
        for extension in cogs:
            self.load_extension(extension)
            print("loaded extension", extension)

    async def log(self, **kwargs):
        await self.wait_until_ready()
        await self.log_channel.send(**kwargs)

    async def on_message(self, message):
        await self.wait_until_ready()
        if message.guild is None or message.author.bot:
            return
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def on_connect(self):
        try:
            self.db = await Database.create_pool(bot=self, uri=postgres, loop=self.loop)
        except OSError:
            print("postgres server is not running")

    async def on_ready(self):
        self.guild = self.get_guild(int(guild))  # guild id here
        print(self.guild)
        self.log_channel = self.guild.get_channel(int(log_channel))  # log channel id
        print(f'Successfully logged in as {self.user}\nSharded to {len(self.guilds)} guilds')
        await self.change_presence(status=discord.Status.online, activity=discord.Game(name='use the prefix "+"'))

    # async def on_command_error(self, context, exception):
    #     if isinstance(exception, CommandNotFound):
    #         await context.send('that is not a command')
    #         return
    #     embed = discord.Embed(title=f"{type(exception).__name__}", colour=discord.Colour.red(),
    #                           description=str(exception))
    #     await self.log(content=f"error from {context.message.jump_url}\n {exception}")
    #     await context.send(embed=embed)

    @classmethod
    async def setup(cls, toke):
        bot = cls()
        try:
            await bot.start(toke)

        except KeyboardInterrupt:
            await bot.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Riser.setup(token))
