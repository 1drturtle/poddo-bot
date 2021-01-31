from discord.ext import commands

from cogs.rpg.models import *
from utils.functions import create_default_embed


class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # character database
        self.cdb = bot.mdb['rpg-characters-db']

    @commands.group(name='rpg', invoke_without_command=True)
    async def rpg(self, ctx):
        """Base command for all RPG commands. Shows status of Character"""
        pass

    @rpg.command(name='setup')
    async def rpg_setup_character(self, ctx):
        """Creates a new character if the user does not already have one."""
        check = await self.cdb.find_one({'owner': ctx.author})
        if check is not None:
            return await ctx.send('You already have a character!')

        char_name = ctx.prompt('Character Name', 'What would you like your character to be called?')

        new_char = Character.new(ctx.author, char_name)
        await new_char.commit(self.cdb)
        embed = create_default_embed(ctx, title='Character Created!', description=f'Your character named {char_name} '
                                                                                  f'has been created!')
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RPG(bot))
