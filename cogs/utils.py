from discord.ext import commands
from datetime import datetime, timedelta
from utils.functions import create_default_embed
from config import PREFIX as BOT_PREFIX


def time_to_readable(delta_uptime: timedelta):
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d, {hours}h, {minutes}m, {seconds}s"


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """
        Gets the ping of the bot.
        """
        now = datetime.now()
        message = await ctx.send('Ping!')
        await message.edit(content=f'Pong!\nBot: {int(ctx.bot.latency*1000)} ms\n'
                                   f'Discord: {int((datetime.now() - now).total_seconds()*1000)} ms')

    @commands.command(name='uptime', aliases=['up', 'alive'])
    async def uptime(self, ctx):
        """
        Displays the current uptime of the bot.
        """
        embed = create_default_embed(ctx)
        embed.title = 'Poddo Uptime'
        bot_up = time_to_readable(self.bot.uptime)
        embed.add_field(name='Bot Uptime', value=f'{bot_up}')
        if ctx.bot.is_ready():
            embed.add_field(name='Ready Uptime',
                            value=f'{time_to_readable(datetime.utcnow() - self.bot.ready_time)}')
        return await ctx.send(embed=embed)

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
                prefix = self.bot.prefixes.get(guild_id, BOT_PREFIX)
            else:
                dbsearch = await self.bot.mdb['prefixes'].find_one({'guild_id': guild_id})
                if dbsearch is not None:
                    prefix = dbsearch.get('prefix', BOT_PREFIX)
                else:
                    prefix = BOT_PREFIX
                self.bot.prefixes[guild_id] = prefix
            return await ctx.send(f'No prefix specified to change. Current Prefix: `{prefix}`')
        else:
            await ctx.bot.mdb['prefixes'].update_one({'guild_id': guild_id},
                                                     {'$set': {'prefix': to_change}}, upsert=True)
            ctx.bot.prefixes[guild_id] = to_change
            return await ctx.send(f'Guild prefix updated to `{to_change}`')


def setup(bot):
    bot.add_cog(Utils(bot))
