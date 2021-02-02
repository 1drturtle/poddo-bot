import io
import logging
import textwrap
import traceback
from contextlib import redirect_stdout

import discord
from discord.ext import commands

from utils.functions import yes_or_no, create_default_embed

log = logging.getLogger(__name__)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.group(name='admin', invoke_without_command=True)
    async def admin(self, ctx):
        """
        Owner-only commands for the bot.
        """
        return await ctx.send('nope.')

    @admin.command(name="restart")
    async def restart(self, ctx):
        """
        Restarts the bot.
        """
        confirm = await ctx.prompt('Confirm', 'Are you sure you want to shutdown the bot?')
        if yes_or_no(confirm):
            log.warning(f'Bot restart initiated by {ctx.author.name}')
            await self.bot.logout()

    # Eval Code
    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

    def embed_split(self, embed, body, color, title='Embed Result'):
        embed.colour = color
        body = body if body is not None else "None"
        error_str = f'```py\n{body}\n```'
        if len(error_str) >= 1010:
            error_str = f'```py\n{body[:1010]} ...\n```'
        embed.title = title
        embed.add_field(name='\u200b', value=error_str)
        return embed

    @admin.command(name='eval')
    async def eval(self, ctx, *, body: str):
        """
        Evaluates input
        """
        embed = create_default_embed(ctx)

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        if not body.startswith('```'):
            body = f'```py\n' \
                   f'{body}\n' \
                   f'```'
        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
            print(repr(env['func']))
        except Exception as e:
            return await ctx.send(embed=self.embed_split(embed, f'{e.__class__.__name__}: {str(e)}',
                                                         discord.Colour.red(), title='Eval Compile Error'))
        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            return await ctx.send(embed=self.embed_split(
                embed,
                f'{value}{traceback.format_exc()}',
                discord.Colour.red(),
                title='Error during Eval'
            ))
        else:
            value = stdout.getvalue()

            embed.title = 'Eval Result'
            embed.colour = discord.Colour.green()
            desc = ''

            if ret is None:
                if value:
                    desc = value
            else:
                self._last_result = ret
                desc = f'{value}{ret}'

            return await ctx.send(embed=self.embed_split(
                embed,
                desc,
                discord.Colour.green(),
                title='Eval Result'
            ))


def setup(bot):
    bot.add_cog(Admin(bot))
