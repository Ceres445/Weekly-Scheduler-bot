import discord
from discord.ext import commands
from aiohttp import ClientSession
import datetime
import asyncio

from cogs.utils.database import Database
cogs = ["cogs.reminder"]


class Reminder(commands.Bot):
    def __init__(self, **kwargs):
        allowed_mentions = discord.AllowedMentions(everyone=False, roles=True, users=True)
        super().__init__(command_prefix=kwargs.pop('command_prefix', ['+']), case_insensitive=True,
                         allowed_mentions=allowed_mentions)
        self.session = ClientSession(loop=self.loop)
        self.start_time = datetime.datetime.utcnow()
        self.clean_text = commands.clean_content(escape_markdown=True, fix_channel_mentions=True)
        self.guild = None
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
            self.db = await Database.create_pool(bot=self, uri="postgresql://localhost/reminder", loop=self.loop)
        except OSError:
            print("postgres server is not running")

    async def on_ready(self):
        self.guild = self.get_guild(697322080135282758)
        self.log_channel = self.guild.get_channel(751047326403002379)
        print(f'Successfully logged in as {self.user}\nSharded to {len(self.guilds)} guilds')
        await self.change_presence(status=discord.Status.online, activity=discord.Game(name='use the prefix "+"'))

    async def on_command_error(self, context, exception):
        await self.log(content=f"error from {context.message.jump_url }\n {exception}")

    @classmethod
    async def setup(cls, token):
        bot = cls()
        try:
            await bot.start(token)

        except KeyboardInterrupt:
            await bot.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Reminder.setup("NzM1MDg0NTg0Mjc4MTYzNTU3.XxbG3g.EgXjEFq-_w_UwRPzUXh0YTM9NF0"))
