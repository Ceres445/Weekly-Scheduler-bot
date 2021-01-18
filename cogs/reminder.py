import asyncio
import json
from datetime import datetime as dt, timedelta

import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime

from .utils.functions import hour_rounder


def embed_class(record, author: discord.Member):
    desc = ''
    for key, value in record.items():
        desc += key + ': ' + value
    embed = discord.Embed(title=f"Class", description=desc)
    embed.set_author(name=author.name, url=author.avatar_url)
    return embed


class reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("cogs/json_files/embeds.json", "r") as f, \
                open("cogs/json_files/time.json", "r") as f2:
            self.embeds = json.load(f)
            self.links = json.load(f2)['links']
        self.channel = None
        self.data = None
        self.remind.start()

    @tasks.loop(minutes=5)
    async def remind(self):
        print(datetime.now().strftime('%H:%M'))
        time = datetime.now().strftime('%H:%M')
        day = datetime.now().weekday()
        print(time, day, "is the time and day")
        print([[x['day'], x['time']] for x in self.data])
        if [day, time] in [[x['day'], x['time']] for x in self.data]:
            record = self.data[[[x['day'], x['time']] for x in self.data].index([day, time])]
            await self.channel.send(content=f"<@&{self.embeds['roles'][record['subject']]}>",
                                    embed=discord.Embed().from_dict(self.embeds[record['subject']]))
            if not record['permanant']:
                await self.bot.db.delete(record)
        else:
            print("check failed")

    @remind.before_loop
    async def before_remind(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(3)
        self.channel = self.bot.guild.get_channel(698792545760706590)
        print(datetime.now().strftime('%H:%M'))
        await self.bot.log(content=f"time is {datetime.now().strftime('%H:%M')}.")
        self.data = await self.bot.db.get_data()
        print([[x['day'], x['time']] for x in self.data], hour_rounder())
        await asyncio.sleep(hour_rounder())

    @commands.command()
    async def next(self, ctx):
        time = datetime.now()
        day = datetime.now().weekday()
        today = list(filter(lambda x: x['day'] == day, self.data))
        strifted = [dt.strptime(x['time'], '%H:%M') for x in today]
        today_time = [dt.now().replace(hour=a.hour, minute=a.minute, second=0, microsecond=0) for a in strifted]
        today_time = sorted(today_time)
        index = self.get_index(today_time, day, time)
        today = list(filter(lambda x: x['day'] == index[1], self.data))
        record = list(filter(lambda x: x['time'] == index[0], today))[0]
        await ctx.send(embed=embed_class(record, ctx.author))

    def get_index(self, today_time, day, time):
        state = 0
        for i in today_time:
            if i >= time:
                index = today_time.index(i)
                state = 1
                break
        if state:
            return today_time[index].strftime('%H:%M'), day
        else:
            if day == 6:
                day = 0
            else:
                day += 1
            today = list(filter(lambda x: x['day'] == day, self.data))
            strifted = [dt.strptime(x['time'], '%H:%M') for x in today]
            today_time = [dt.now().replace(hour=a.hour, minute=a.minute, second=0, microsecond=0) for a in strifted]
            today_time = sorted(today_time)
            time = time + timedelta(hours=24)
            time.replace(hour=0, minute=0, second=0, microsecond=0)
            return self.get_index(today_time, day, time)

    @commands.command()
    async def embed(self, ctx, subject: str = "phy_"):
        await ctx.send(embed=discord.Embed.from_dict(self.embeds[subject]))


def setup(bot):
    bot.add_cog(reminder(bot))
