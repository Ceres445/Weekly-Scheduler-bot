import asyncio
import json
from datetime import datetime
from datetime import timedelta

import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import BadArgument

from cogs.reminder import get_attendee
from cogs.utils.functions import hour_rounder, get_pings, get_attendee_name, get_name, get_days
from cogs.utils.menu import ExamMenu


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
        await self.exam_reload()
        today = datetime.now().date(), 1
        five_day = (datetime.now() + timedelta(days=5)).date(), 2
        two_day = (datetime.now() + timedelta(days=2)).date(), 3
        for a, delta in ([today, five_day, two_day], [0, 5, 2]):
            for record in [x for x in self.test_data if x['data'] - timedelta(days=delta)]:
                await self.channel.send(get_pings(record['attendees']), embed=self.test_embed(record, get_name(a[1])))
                if delta == 0:
                    await self.bot.db.remove_test(record)

    @remind_test.before_loop
    async def before_remind_test(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(3)
        self.channel = self.bot.guild.get_channel(698792545760706590)
        await self.bot.log(content=f"test cogs loop started.")
        self.test_data = await self.bot.db.get_test_data()
        # await asyncio.sleep(hour_rounder(day=True))

    @commands.group(invoke_without_command=True, aliases=['test'])
    async def exam(self, ctx, pid=None):
        """Shows test info"""
        if self.test_data is None:
            await self.exam_reload(ctx)
        if pid is None:
            menu = ExamMenu(self.test_data)
            await menu.start(ctx)
        else:
            record = await self.bot.db.fetchrow("SELECT * FROM test_data WHERE pid=$1", int(pid))
            if record is None:
                await ctx.send('incorrect pid')
                return
            await ctx.send(embed=self.test_embed(record, get_days(record['date'])))

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

    @exam.command()
    async def add(self, ctx, date, subject, attendees: str = 'all'):
        date = datetime.strptime(date, '%Y-%m-%d')
        await self.bot.db.execute("INSERT INTO test_data (date, subject, attendees) VALUES ($1, $2, $3)", date, subject,
                                  attendees)
        await ctx.send('added to database')

    @commands.is_owner()
    @exam.command()
    async def remove(self, ctx, pid):
        await self.bot.db.execute("DELETE FROM test_data WHERE pid=$1", int(pid))
        await ctx.send('removed test')

    @exam.command()
    async def data(self, ctx, pid, key, *, value):
        record = await self.bot.db.fetchrow("SELECT * FROM test_data WHERE pid = $1", int(pid))
        if record is None:
            await ctx.send('test pid doesnt exist')
            return
        else:
            await self.bot.db.execute("UPDATE test_data set data=$1 WHERE pid=$2", json.dumps({key: value}), int(pid))
            await ctx.send('updated database')

    @commands.is_owner()
    @exam.command(name='reload')
    async def exam_reload(self, ctx=None):
        self.test_data = await self.bot.db.get_test_data()
        if ctx is not None:
            await ctx.send('loaded test data')

    def test_embed(self, record, desc):

        if desc == 'today':
            color = discord.Color.red()
        else:
            color = discord.Embed.Empty
        embed = discord.Embed(title=f"Test {desc}",
                              description=f"Test in {self.converter['subjects'][record['subject']]} for"
                                          f" {get_attendee_name(record['attendees'])} students",
                              color=color)
        embed.add_field(name="Test Date", value=record['date'])
        print(record['data'])
        if record['data'] is not None:
            data = json.loads(record['data'])
            for key, value in data.items():
                embed.add_field(name=key, value=value.replace('\\n', '\n'), inline=False)
        embed.set_footer(text='Use `+test` for more info')
        return embed


def setup(bot):
    bot.add_cog(Tests(bot))
