import asyncio
import json
from datetime import datetime as dt, timedelta

import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime

from .utils.functions import hour_rounder


def convert_record(self, record):
    record = dict(record)
    for key, value in record.items():
        if key == 'day':
            record[key] = self.converter['day_name'][value]
        if key == 'subject':
            record[key] = self.converter['subjects'][value]
        if key == 'attendees':
            if value == 'int':
                record[key] = 'Integrated'
            else:
                record[key] = "CRP"
    record.pop('permanant')
    return record


def embed_class(self, record, author: discord.Member):
    desc = ''
    record = convert_record(self, record)
    subject = record['subject']
    record.pop('subject')
    attendee = record['attendees']
    record.pop('attendees')
    for key, value in record.items():
        desc += str(key).capitalize() + ': ' + str(value) + '\n'
    if record['day'] == self.converter['day_name'][dt.now().weekday()]:
        typer = "today"
    else:
        typer = 'tomorrow'
    embed = discord.Embed(title=f"{subject} class {typer} for {attendee} ", description=desc, timestamp=dt.utcnow())
    embed.set_footer(text=f'Invoked by {author.name}', icon_url=author.avatar_url)
    return embed


def embeds_class(self, today, author, typer):
    base = convert_record(self, today[0])
    embed = discord.Embed(title=f"Classes {typer} on {base['day']} for {base['attendees']}",
                          timestamp=dt.utcnow())
    today = sorted(today, key=lambda x: x['time'])
    for record in today:
        record = convert_record(self, record)
        subject = record['subject']
        record.pop('subject')
        record.pop('day')
        record.pop('attendees')
        desc = ''
        for key, value in record.items():
            desc += str(key) + ': ' + str(value) + '\n'
        embed.add_field(name=subject + ' class', value=desc, inline=False)
    embed.set_footer(text=f'Invoked by {author.name}', icon_url=author.avatar_url)
    return embed


class NotStudent(commands.CommandError):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text


def get_attendee(roles):
    roles = [role.id for role in roles]
    if 698791878421774397 in roles:
        return 'crp'
    elif 698791917026017291 in roles:
        return 'int'
    else:
        raise NotStudent("You must have Integrated or CRP role to use this command")


class reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("cogs/json_files/embeds.json", "r") as f, \
                open("cogs/json_files/time.json", "r") as f2:
            self.embeds = json.load(f)
            self.converter = json.load(f2)
            self.links = self.converter['links']
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

    @commands.is_owner()
    async def reload(self, ctx):
        self.data = await self.bot.db.get_data()
        await ctx.send('loaded')

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
        """Shows the next class that will happen"""
        attendee = get_attendee(ctx.author.roles)
        time = datetime.now()
        day = datetime.now().weekday()
        today = list(filter(lambda x: x['day'] == day, self.data))
        today = list(filter(lambda x: x['attendees'] == attendee, today))
        strifted = [dt.strptime(x['time'], '%H:%M') for x in today]
        today_time = [dt.now().replace(hour=a.hour, minute=a.minute, second=0, microsecond=0) for a in strifted]
        today_time = sorted(today_time)
        index = self.get_index(today_time, day, time, attendee)
        today = list(filter(lambda x: x['day'] == index[1], self.data))
        record = list(filter(lambda x: x['time'] == index[0], today))[0]
        await ctx.send(embed=embed_class(self, record, ctx.author))

    def get_index(self, today_time, day, time, attendee):
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
            today = list(filter(lambda x: x['attendees'] == attendee, today))
            strifted = [dt.strptime(x['time'], '%H:%M') for x in today]

            time = time + timedelta(hours=24)
            time = time.replace(hour=0, minute=0, second=0, microsecond=0)
            today_time = [time.replace(hour=a.hour, minute=a.minute, second=0, microsecond=0) for a in strifted]
            today_time = sorted(today_time)
            print(time, today_time)
            return self.get_index(today_time, day, time)

    @commands.command()
    async def today(self, ctx):
        """Shows the classes that are happening today"""
        attendee = get_attendee(ctx.author.roles)
        day = datetime.now().weekday()
        today = list(filter(lambda x: x['day'] == day, self.data))
        today = list(filter(lambda x: x['attendees'] == attendee, today))
        await ctx.send(embed=embeds_class(self, today, ctx.author, 'today'))

    @commands.command(aliases=['tmr'])
    async def tomorrow(self, ctx):
        """Shows the classes that will happen tomorrow"""
        attendee = get_attendee(ctx.author.roles)
        day = (datetime.now() + timedelta(hours=24)).weekday()
        today = list(filter(lambda x: x['day'] == day, self.data))
        today = list(filter(lambda x: x['attendees'] == attendee, today))
        await ctx.send(embed=embeds_class(self, today, ctx.author, 'tomorrow'))

    @commands.command(description="valid subjects are phy, comp, chem, eng, bio, math")
    async def embed(self, ctx, subject: str = "phy_"):
        """Shows the embed for any subject"""
        try:
            if len(subject) == 3:
                await ctx.send(embed=discord.Embed.from_dict(self.embeds[subject + '_']))
            else:
                await ctx.send(embed=discord.Embed.from_dict(self.embeds[subject]))
        except KeyError:
            await ctx.send(f'<@339365580496830466> {ctx.author.mention} thats not a valid subject use '
                           f'+help embed for info')


def setup(bot):
    bot.add_cog(reminder(bot))
