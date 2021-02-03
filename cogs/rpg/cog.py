from discord.ext import commands


class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # character database
        self.cdb = bot.mdb['rpg-characters-db']

    @commands.group(name='rpg', invoke_without_command=True)
    async def rpg(self, ctx):
        """Base command for all RPG commands. Shows status of Character"""
        raise NotImplementedError()


def setup(bot):
    bot.add_cog(RPG(bot))
