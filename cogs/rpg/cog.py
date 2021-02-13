from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from utils.functions import create_default_embed, yes_or_no
import discord
from random import randint
from cogs.rpg.models.character import Character, xp_for_level
import math


def no_character_embed(ctx, title=None, desc=None):
    embed = create_default_embed(ctx, colour=discord.Colour.red())
    embed.title = title or 'You must have a character to run this command!'
    embed.description = desc or f'Create a character with `{ctx.prefix}rpg setup`'
    return embed


class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # character database
        self.cdb = bot.mdb['rpg-characters-db']

    @commands.group(name='rpg', invoke_without_command=True, aliases=['game', 'g'])
    async def rpg(self, ctx):
        """Base command for all RPG commands. Shows status of Character"""
        char = await ctx.get_character()
        if not char:
            return await ctx.send(embed=no_character_embed(ctx))
        embed = create_default_embed(ctx)
        embed.title = 'Character Info!'
        embed.add_field(name='Name', value=char.name)
        embed.add_field(name='Level Info', value=char.level_str())
        embed.add_field(name='Gold', value=f'{char.gold} gp')
        return await ctx.send(embed=embed)

    @rpg.command(name='setup')
    async def rpg_setup(self, ctx):
        """Creates a character."""
        char = await ctx.get_character()
        if char:
            return await ctx.send(embed=no_character_embed(
                ctx,
                title='You already have a character!',
                desc='You cannot create a character, as you already have one.'
            )
            )
        char_name = await ctx.prompt(
            title='What should your character be called?',
            description='Enter your character\'s name!'
        )
        if char_name is None:
            return await ctx.send('Character name prompt timed out, re-run the command to try again.',
                                  delete_after=15)
        if not all(x.isalpha() or x.isspace() for x in char_name):
            return await ctx.send(
                'Invalid character name! Only letters and spaces are allowed (no symbols or numbers).',
                delete_after=15)
        char = Character.new(char_name, owner_id=ctx.author.id)
        await char.commit(self.cdb)
        embed = create_default_embed(ctx)
        embed.title = 'Your character has been created!'
        embed.description = f'{char.name}\n{char.level_str()}'
        return await ctx.send(embed=embed)

    @rpg.command(name='delete')
    async def rpg_delete(self, ctx):
        """Deletes a character."""
        char = await ctx.get_character()
        if not char:
            return await ctx.send(embed=no_character_embed(
                ctx,
                title='You do not have a character!',
                desc='You cannot delete your character, as you do not have one.'
            )
            )
        confirm = await ctx.prompt(
            title='Are you sure you want to delete your character?',
            description='This action is irrevocable!'
        )
        if not yes_or_no(confirm):
            return await ctx.send('Cancelling.', delete_after=10)
        await self.cdb.delete_one({'owner_id': ctx.author.id})
        return await ctx.send(embed=create_default_embed(ctx, title='Your character has been deleted.',
                                                         description=f'Say goodbye to {char.name}!'))

    # --------------------------
    # Work Commands
    # --------------------------

    @rpg.command(name='fish')
    @commands.cooldown(1, 300, BucketType.user)
    async def rpg_fish(self, ctx):
        """
        Fish for XP

        Gives XP and a little bit of gold, 5 minute cooldown.
        """
        char = await ctx.get_character()
        if not char:
            return await ctx.send(embed=no_character_embed(ctx))

        # XP should be between 3-5% of xp between current and next level
        next_xp = xp_for_level(char.level + 1) - xp_for_level(char.level)
        lower = math.floor(next_xp * 0.03)
        upper = math.floor(next_xp * 0.05)
        xp = randint(lower, upper)
        xp_result = char.mod_xp(xp)

        # Gold will be 10 +/- (15 * 5% of current level)
        bound = 15 + math.floor((char.level * 0.05))
        gold = randint(max(0, 10 - bound), 10 + bound)
        char.gold += gold

        embed = create_default_embed(ctx)
        embed.title = f'{char.name} goes Fishing!'
        embed.add_field(name='Gold', value=f'{char.gold} (+{gold})')
        embed.add_field(name='XP', value=f'{char.xp} (+{xp})')
        # did we level?
        if xp_result:
            embed.add_field(name='Level Up!', value=f'You are now level {char.level}!')

        # save & exit
        await char.commit(self.cdb)
        return await ctx.send(embed=embed)

    # --------------------------
    # Admin Commands
    # --------------------------
    @commands.group(name='dev', invoke_without_subcommand=True, hidden=True)
    async def dev(self, ctx):
        """Commands for the Developer."""
        pass


def setup(bot):
    bot.add_cog(RPG(bot))
