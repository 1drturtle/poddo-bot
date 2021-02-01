from discord.ext import commands

from utils.functions import create_default_embed, yes_or_no


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='admin', invoke_without_command=True)
    @commands.is_owner()
    async def admin(self, ctx):
        """
        Owner-only commands for the bot.
        """
        return await ctx.send('nope.')

    @admin.command(name="restart")
    @commands.is_owner()
    async def restart(self, ctx):
        """
        Restarts the bot.
        """
        confirm = await ctx.prompt('Confirm', 'Are you sure you want to shutdown the bot?')
        if yes_or_no(confirm):
            await self.bot.logout()

    @commands.command(name='prefix')
    @commands.check_any(commands.has_guild_permissions(manage_guild=True), commands.is_owner())
    @commands.guild_only()
    async def change_prefix(self, ctx, to_change: str = None):
        """
        Changes the prefix for the current guild.
        Can only be ran in a guild. If no prefix is specified, will show the current prefix.
        Requires Manage Server permissions.
        """
        guild_id = str(ctx.guild.id)
        if to_change is None:
            if guild_id in self.bot.prefixes:
                prefix = self.bot.prefixes.get(guild_id, self.bot.prefix)
            else:
                dbsearch = await self.bot.mdb['prefixes'].find_one({'guild_id': guild_id})
                if dbsearch is not None:
                    prefix = dbsearch.get('prefix', self.bot.prefix)
                else:
                    prefix = self.bot.prefix
                self.bot.prefixes[guild_id] = prefix
            return await ctx.send(f'No prefix specified to Change. Current Prefix: `{prefix}`')
        else:
            await ctx.bot.mdb['prefixes'].update_one({'guild_id': guild_id},
                                                     {'$set': {'prefix': to_change}}, upsert=True)
            ctx.bot.prefixes[guild_id] = to_change
            return await ctx.send(f'Guild prefix updated to `{to_change}`')


def setup(bot):
    bot.add_cog(Admin(bot))
