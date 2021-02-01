from discord.ext import commands
from datetime import datetime, timedelta
from utils.functions import create_default_embed


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


def setup(bot):
    bot.add_cog(Utils(bot))
