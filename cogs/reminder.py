import asyncio
import json
from datetime import datetime as dt, timedelta

import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime

from discord.ext.commands import BadArgument, Paginator

from cogs.utils.functions import hour_rounder
from cogs.utils.get_html import get_string


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
    if record['day'] == dt.now().weekday():
        typer = "today"
    elif record['day'] == dt.now().weekday() + 1 or (dt.now().weekday() == 6 and record['day'] == 0):
        typer = 'tomorrow'
    else:
        typer = "a few days from now"
    record = convert_record(self, record)
    subject = record['subject']
    record.pop('subject')
    attendee = record['attendees']
    record.pop('attendees')
    for key, value in record.items():
        desc += str(key).capitalize() + ': ' + str(value) + '\n'

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

    @commands.command()
    async def html(self, ctx):
        data = sorted(self.data, key=lambda x: (x['day'], x['time']))
        data = [convert_record(self, record) for record in data]
        img = get_string(data)
        page = Paginator(prefix='```html')
        page.add_line(img[:1990])
        page.add_line(img[1990:])
        for kage in page.pages:
            await ctx.send(kage)
        # embed = discord.Embed()
        # file = discord.File(fp=img, filename="table.png")
        # embed.set_image(url="attachment://table.png")
        # await ctx.send(file=file, embed=embed)

    @tasks.loop(minutes=5)
    async def remind(self):
        time = datetime.now().strftime('%H:%M')
        day = datetime.now().weekday()
        print(time, day, "is the time and day")
        if [day, time] in [[x['day'], x['time']] for x in self.data]:
            record = self.data[[[x['day'], x['time']] for x in self.data].index([day, time])]
            await self.channel.send(content=f"<@&{self.embeds['roles'][record['attendees']]}>",
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
        await self.bot.log(content=f"time is {datetime.now().strftime('%H:%M')}.")
        self.data = await self.bot.db.get_data()
        await asyncio.sleep(hour_rounder())

    @commands.command()
    async def next(self, ctx, attendee: str = None):
        if attendee is None:
            attendee = get_attendee(ctx.author.roles)
        elif attendee.lower().strip() not in ('crp', 'int'):
            raise BadArgument("attendee: should be int or crp")
        else:
            attendee = attendee.lower().strip()[:3]
        """Shows the next class that will happen"""
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
        index = 0
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
            return self.get_index(today_time, day, time, attendee)

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx):
        self.data = await self.bot.db.get_data()
        await ctx.send('loaded')

    @commands.command()
    async def today(self, ctx, attendee: str = None):
        """Shows the classes that are happening today"""
        if attendee is None:
            attendee = get_attendee(ctx.author.roles)
        elif attendee.lower().strip() not in ('crp', 'int'):
            raise BadArgument("attendee: should be int or crp")
        else:
            attendee = attendee.lower().strip()[:3]
        day = datetime.now().weekday()
        today = list(filter(lambda x: x['day'] == day, self.data))
        today = list(filter(lambda x: x['attendees'] == attendee, today))
        if len(today) == 0:
            await ctx.send("No classes today :)")
            return
        await ctx.send(embed=embeds_class(self, today, ctx.author, 'today'))

    @commands.command(aliases=['tmr'])
    async def tomorrow(self, ctx, attendee: str = None):
        """Shows the classes that will happen tomorrow"""
        if attendee is None:
            attendee = get_attendee(ctx.author.roles)
        elif attendee.lower().strip()[:3] not in ('crp', 'int'):
            raise BadArgument("attendee: should be int or crp")
        else:
            attendee = attendee.lower().strip()[:3]
        day = (datetime.now() + timedelta(hours=24)).weekday()
        today = list(filter(lambda x: x['day'] == day, self.data))
        today = list(filter(lambda x: x['attendees'] == attendee, today))
        if len(today) == 0:
            await ctx.send("No classes tomorrow :)")
            return
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
            await ctx.send(f'<@339365580496830466> {ctx.author.mention} that is not a valid subject use '
                           f'+help embed for info')


def setup(bot):
    bot.add_cog(reminder(bot))
