from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from utils.functions import create_default_embed
import discord
from random import randint
from cogs.rpg.models.character import Character
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

    @commands.group(name='rpg', invoke_without_command=True)
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
            return await ctx.send(embed=no_character_embed(ctx,
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
            return await ctx.send('Invalid character name! Only letters and spaces are allowed (no symbols or numbers).',
                                  delete_after=15)
        char = Character.new(char_name, owner_id=ctx.author.id)
        await char.commit(self.cdb)
        embed = create_default_embed(ctx)
        embed.title = 'Your character has been created!'
        embed.description = f'{char.name}\n{char.level_str()}'
        return await ctx.send(embed=embed)

    # --------------------------
    # Work Commands (Cooldowns!)
    # --------------------------

    @rpg.command(name='mine')
    @commands.cooldown(1, 300, BucketType.user)
    async def rpg_mine(self, ctx):
        """
        Mine ores for gold!

        Gives gold and a small amount of XP. On a 5 minute cooldown.
        """
        char = await ctx.get_character()
        if not char:
            return await ctx.send(embed=no_character_embed(ctx))

        GOLD_SCALE_VALUE = 0.03
        XP_SCALE_VALUE = 0.01

        # ideally we want to scale the gold with level
        # current scale is 3% per level
        gold_lower_bound = math.floor(30 * (1 + (char.level * GOLD_SCALE_VALUE)))
        gold_upper_bound = math.floor(60 * (1 + (char.level * GOLD_SCALE_VALUE)))
        gold = randint(gold_lower_bound, gold_upper_bound)
        char.gold += gold

        # we don't want much XP from mining
        # current scale is 1% per level
        xp_lower_bound = math.floor(10 * (1 + (char.level * XP_SCALE_VALUE)))
        xp_upper_bound = math.floor(30 * (1 + (char.level * XP_SCALE_VALUE)))
        xp = randint(xp_lower_bound, xp_upper_bound)
        # store our mod result
        xp_result = char.mod_xp(xp)

        embed = create_default_embed(ctx)
        embed.title = f'{char.name} goes Mining!'
        embed.add_field(name='Gold', value=f'{char.gold} (+{gold})')
        embed.add_field(name='XP', value=f'{char.xp} (+{xp})')
        # did we level?
        if xp_result:
            embed.add_field(name='Level Up!', value=f'You are now level {char.level}!')

        # save & exit
        await char.commit(self.cdb)
        return await ctx.send(embed=embed)

    @rpg.command(name='fish')
    @commands.cooldown(1, 180, BucketType.user)
    async def rpg_fish(self, ctx):
        """
        Go to the ocean and fish

        Gives XP and a small amount of gold. On a 3 minute cooldown.
        """
        char = await ctx.get_character()
        if not char:
            return await ctx.send(embed=no_character_embed(ctx))

        GOLD_SCALE_VALUE = 0.01
        XP_SCALE_VALUE = 0.03

        # current scale is 3% per level
        gold_lower_bound = math.floor(10 * (1 + (char.level * GOLD_SCALE_VALUE)))
        gold_upper_bound = math.floor(20 * (1 + (char.level * GOLD_SCALE_VALUE)))
        gold = randint(gold_lower_bound, gold_upper_bound)
        char.gold += gold

        # current scale is 1% per level
        xp_lower_bound = math.floor(30 * (1 + (char.level * XP_SCALE_VALUE)))
        xp_upper_bound = math.floor(60 * (1 + (char.level * XP_SCALE_VALUE)))
        xp = randint(xp_lower_bound, xp_upper_bound)
        # store our mod result
        xp_result = char.mod_xp(xp)

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


def setup(bot):
    bot.add_cog(RPG(bot))
