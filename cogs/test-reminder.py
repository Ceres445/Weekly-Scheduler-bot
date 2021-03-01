import asyncio
import json
from datetime import datetime
from datetime import timedelta

import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import BadArgument
from tabulate import tabulate

from cogs.reminder import get_attendee
from cogs.utils.functions import hour_rounder


def get_pings(attendees: str):
    if attendees == 'int':
        return f"<@&815982951946125363>"
    elif attendees == 'crp':
        return f"<@&698791878421774397>"
    else:
        return f"<@&815982951946125363>" + f"<@&698791878421774397>"


def get_attendee_name(param):
    if param == 'int':
        return 'Integrated'
    elif param == 'crp':
        return "CRP"
    else:
        return param


def get_name(a):
    if a == 1:
        return 'today'
    elif a == 2:
        return 'in five days'
    else:
        return 'in two days'


def get_days(date: datetime.date):
    if date == datetime.now().date():
        return 'today'
    else:
        return f'in {(date - datetime.now().date()).days} days'


class Tests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.test_data = None
        with open("cogs/json_files/embeds.json", "r") as f, \
                open("cogs/json_files/time.json", "r") as f2:
            self.embeds = json.load(f)
            self.converter = json.load(f2)
            self.links = self.converter['links']
        self.remind_test.start()

    @tasks.loop(minutes=60 * 24)
    async def remind_test(self):
        print('test loop started')
        today = datetime.now().date(), 1
        five_day = (datetime.now() + timedelta(days=5)).date(), 2
        two_day = (datetime.now() + timedelta(days=2)).date(), 3
        for a in [today, five_day, two_day]:
            if a[0] in [x['date'] for x in self.test_data]:
                record = self.test_data[[x['date'] for x in self.test_data].index(a[0])]
                await self.channel.send(get_pings(record['attendees']), embed=self.test_embed(record, get_name(a[1])))
                await self.bot.db.remove_test(record)
                await self.remind_test()

    @remind_test.before_loop
    async def before_remind_test(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(3)
        self.channel = self.bot.guild.get_channel(698792545760706590)
        await self.bot.log(content=f"test cogs loop started.")
        self.test_data = await self.bot.db.get_test_data()
        await asyncio.sleep(hour_rounder(day=True))

    @commands.group(invoke_without_command=True, aliases=['test'])
    async def exam(self, ctx):
        """Shows test info"""
        if self.test_data is None:
            await self.exam_reload(ctx)
        converted = [(record['pid'], record['subject'], record['date'],
                      get_attendee_name(record['attendees'])) for record in self.test_data]

        string = tabulate(converted)
        await ctx.send(f'```prolog\n{string}\n```')

    @exam.command(name='next')
    async def exam_next(self, ctx, attendee: str = None):
        """Shows the next class that will happen"""
        if attendee is None:
            attendee = get_attendee(ctx.author.roles)
        elif attendee.lower().strip() not in ('crp', 'int'):
            raise BadArgument("attendee: should be int or crp")
        else:
            attendee = attendee.lower().strip()[:3]
        data = sorted(self.test_data, key=lambda x: x['date'])
        state = 0
        for i in data:
            if i['date'] < datetime.now().date():
                continue
            else:
                if i['attendees'] == attendee or i['attendees'] == 'all' or attendee == 'all':
                    await ctx.send(embed=self.test_embed(i, get_days(i['date'])))
                    state = 1
                    break
        if not state:
            await ctx.send("no test scheduled")

    @commands.is_owner()
    @exam.command(name='reload')
    async def exam_reload(self, ctx):
        self.test_data = await self.bot.db.get_test_data()
        await ctx.send('loaded')

    def test_embed(self, record, desc):
        if desc == 'today':
            color = discord.Color.red()
        else:
            color = discord.Embed.Empty
        embed = discord.Embed(title=f"Test {desc}", description=f"Test in {self.converter['subjects'][record['subject']]} for"
                                                                f" {get_attendee_name(record['attendees'])} students",
                              color=color)
        embed.add_field(name="Test Date", value=record['date'])
        return embed


def setup(bot):
    bot.add_cog(Tests(bot))
