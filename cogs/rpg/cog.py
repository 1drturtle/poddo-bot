from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from utils.functions import create_default_embed, yes_or_no
import discord
from cogs.rpg.models.character import Character
import random


def no_character_embed(ctx, title=None, desc=None):
    embed = create_default_embed(ctx, colour=discord.Colour.red())
    embed.title = title or 'You must have a character to run this command!'
    embed.description = desc or f'Create a character with `{ctx.prefix}rpg setup`'
    return embed


RARITY_DENOMINATOR = 100


def get_random_item(possibles):
    rand = random.random()
    cumulative_probability = 0
    for item in possibles:
        cumulative_probability += item['rarity']/RARITY_DENOMINATOR
        if rand <= cumulative_probability:
            return item


class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # character database
        self.cdb = bot.mdb['rpg-characters-db']
        # fish db
        self.fish_db = bot.mdb['rpg-fish-db']
        # statistics db
        self.stats_db = bot.mdb['rpg-stats-db']

    async def update_stat(self, _id: int, stat: str):
        await self.stats_db.update_one({'_id': _id}, {'$inc': {stat: 1}}, upsert=True)

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

        # Prompt the User for the Character's Name.
        char_name = await ctx.prompt(
            title='What should your character be called?',
            description='Enter your character\'s name!'
        )
        # Error if we don't get a name or if the name if invalid.
        if char_name is None:
            return await ctx.send('Character name prompt timed out, re-run the command to try again.',
                                  delete_after=15)
        if not all(x.isalpha() or x.isspace() for x in char_name):
            return await ctx.send(
                'Invalid character name! Only letters and spaces are allowed (no symbols or numbers).',
                delete_after=15)

        # Create a default character.
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
    # --    Work Commands     --
    # --------------------------
    @rpg.command(name='fish')
    @commands.cooldown(1, 300, BucketType.user)
    async def rpg_fish(self, ctx):
        """Goes Fishing! Grants XP based on the tier of fish and the rarity of fish."""
        char: Character = await ctx.get_character()
        if char is None:
            return await ctx.send(embed=no_character_embed(ctx))

        # update stats
        await self.update_stat(ctx.author.id, 'fishing')

        # get the fishies
        tier = char.get_stat('fishing') or 1
        fishies = await self.fish_db.find({'tier': tier}).to_list(length=None)

        # which fishy for us?
        fishy = get_random_item(fishies)

        # xp is a function of rarity and character level
        xp = (100 - fishy['rarity']) * (1 + round(char.level/100, 2))
        xp_result = char.mod_xp(xp)
        level_str = ''
        if xp_result and xp_result is not None:
            level_str = f'\nLevel up! You are now level {char.level}.'
        elif not xp_result and xp_result is not None:
            level_str = f'\nLevel Down... You are now level {char.level}.'

        await char.commit(self.cdb)

        embed = create_default_embed(ctx)
        embed.title = f'{char.name} goes Fishing!'
        embed.description = f'{char.name} goes fishing and catches a {fishy["name"]}!'
        embed.add_field(name='XP', value=f'`{(100 - fishy["rarity"])} * {(1 + round(char.level/100, 2))}` = `{xp:+}`')
        embed.add_field(name='Level', value=f'{char.level_str()}{level_str}')

        return await ctx.send(embed=embed)

    # --------------------------
    # ---   Admin Commands   ---
    # --------------------------
    @commands.group(name='dev', invoke_without_subcommand=True, hidden=True)
    async def dev(self, ctx):
        """Commands for the Developer."""
        pass


def setup(bot):
    bot.add_cog(RPG(bot))
