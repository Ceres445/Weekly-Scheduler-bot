from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        await ctx.send("Riser is a bot created to help the students in the rise discord server :)")

    @commands.command()
    async def credits(self, ctx):
        await ctx.send(f"Created by Ceres, pfp credit Blitz")


def setup(bot):
    bot.add_cog(Misc(bot))
