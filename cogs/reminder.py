import asyncio
import json

from discord.ext import commands
from discord.ext import tasks
from datetime import datetime

from .utils.functions import hour_rounder


class reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.remind.start()

    @tasks.loop(minutes=15)
    async def remind(self):
        print(datetime.now().strftime('%H:%M'))
        time = datetime.now().strftime('%H:%M')
        day = datetime.now().day
        if [day, time] in [[x['day'], x['time']] for x in self.data]:
            record = self.data[[[x['day'], x['time']] for x in self.data].index([day, time])]
            await self.channel.send(content=f"<@&{self.embeds['roles'][record['subject']]}>",
                                    embed=self.embeds[record['subject']])
            if not record['permanant']:
                await self.bot.db.delete(record)
        else:
            print("check failed")

    @remind.before_loop
    async def before_remind(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(3)
        with open("cogs/json/embeds.json", "r") as f, \
                open("cogs/json/time.json", "r") as f2:
            self.embeds = json.load(f)
            self.links = json.load(f2)['links']
        self.channel = self.bot.guild.get_channel(698792545760706590)
        print(datetime.now().strftime('%H:%M'))
        await self.bot.log(content=f"time is {datetime.now().strftime('%H:%M')}")
        print(datetime.now().strftime('%H:%M'), 2)
        self.data = await self.bot.db.get_data()
        await asyncio.sleep(hour_rounder())


def setup(bot):
    bot.add_cog(reminder(bot))

