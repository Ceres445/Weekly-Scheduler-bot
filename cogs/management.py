import json

from discord.ext import commands
from tabulate import tabulate


class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("cogs/json_files/embeds.json", "r") as f, \
                open("cogs/json_files/time.json", "r") as f2:
            self.embeds = json.load(f)
            self.converter = json.load(f2)
            self.links = self.converter['links']
            self.data = None

    @commands.Cog.listener('on_ready')
    async def foo(self):
        self.bot.remove_command('order')

    @commands.is_owner()
    @commands.command()
    async def order(self, ctx):
        """Temp command to reset database with usable pid\n Warning dont use without understanding"""

        data = await self.bot.db.get_data()
        data = sorted(data, key=lambda x: (x['day'], x['time']))
        await self.bot.db.execute("DELETE FROM time_data")
        await self.bot.db.execute("ALTER SEQUENCE time_data_pid_seq RESTART WITH 1")
        for record in data:
            await self.bot.db.execute("INSERT INTO time_data (day, time, subject, attendees) VALUES ($1, $2, $3, $4)",
                                      record['day'], record['time'], record['subject'], record['attendees'])
            await ctx.send(f"added {str(record['day']) + record['time'] + record['subject'] + record['attendees']}")

    @commands.is_owner()
    @commands.command(aliases=['show'])
    async def show_all(self, ctx):
        """shows all entries in db"""
        self.data = await self.bot.db.get_data()
        converted = [(self.converter['day_name'][record['day']], record['subject'], record['time'], record['attendees'],
                      record['pid']) for record in self.data]
        string = tabulate(converted)
        await ctx.send(f'```prolog\n{string}\n```')

    @commands.command(aliases=['delete'])
    async def remove(self, ctx, pid):
        """permanently removes a class"""
        pids = await self.bot.db.fetch("SELECT DISTINCT pid FROM time_data")
        if pid in pids:
            await self.bot.db.execute("DELETE FROM time_data WHERE pid=$1", pid)
            await ctx.send('removed')
            return
        await ctx.send('that is not valid pid')

    @commands.command()
    async def switch(self, ctx, pid1: int, pid2: int, perm: bool = False):
        """switches subjects of two classes"""
        pids = await self.bot.db.fetch("SELECT DISTINCT pid FROM time_data")
        pids = [code['pid'] for code in pids]
        if pid1 in pids and pid2 in pids:
            if not perm:
                await self.bot.db.execute("UPDATE time_data set permanant = false, switch = $2 WHERE pid = $1",
                                          pid1, pid2)
                await self.bot.db.execute("UPDATE time_data set permanant = false, switch = $2 WHERE pid = $1",
                                          pid2, pid1)
                await ctx.send('switched for one day')
                reminder = self.bot.get_cog('reminder')
                await reminder.reload(ctx)
                return
            else:
                records = await self.bot.db.fetch("SELECT * FROM time_data WHERE pid=$1 or pid = $2", pid1, pid2)
                print(records[1]['subject'], pid1)
                await self.bot.db.execute("UPDATE time_data set subject = $1 WHERE pid = $2", records[1]['subject'],
                                          pid1)
                await self.bot.db.execute("UPDATE time_data set subject = $1 WHERE pid = $2", records[0]['subject'],
                                          pid2)
                reminder = self.bot.get_cog('reminder')
                await reminder.reload(ctx)
                return
        await ctx.send('that is not valid pid')

    @commands.command()
    async def cancel(self, ctx, pid):
        """cancels a class once"""
        pids = await self.bot.db.fetch("SELECT DISTINCT pid FROM time_data")
        pids = [pid['pid'] for pid in pids]
        if pid in pids:
            await self.bot.db.execute("UPDATE time_data set permanant = false WHERE pid = $1", pid)
            await ctx.send('cancelled')
            return
        await ctx.send('that is not valid pid')


def setup(bot):
    bot.add_cog(Manager(bot))
