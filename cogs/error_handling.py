import discord
import traceback
import sys
from discord.ext import commands
import sentry_sdk
import logging
import pendulum
from utils.functions import create_default_embed

log = logging.getLogger(__name__)


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def log_error(self, error=None, context=None):
        # https://github.com/avrae/avrae/blob/master/dbot.py#L114
        if self.bot.sentry_url is None and self.bot.environment != 'testing':
            log.warning('SENTRY Error Handling is not setup.')
            return

        with sentry_sdk.push_scope() as scope:
            scope.user = {"id": context.author.id, "username": str(context.author)}
            scope.set_tag("message.content", context.message.content)
            scope.set_tag("is_private_message", context.guild is None)
            scope.set_tag("channel.id", context.channel.id)
            scope.set_tag("channel.name", str(context.channel))
            if context.guild_id is not None:
                scope.set_tag("guild.id", context.guild_id)
                scope.set_tag("guild.name", str(context.guild))
            sentry_sdk.capture_exception(error)
            log.info('Error logged to SENTRY')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: utils.Context.PoddoContext
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        # Set up the Error Embed
        embed = create_default_embed(ctx, colour=discord.Colour.red())

        if isinstance(error, commands.DisabledCommand):
            embed.title = 'Command Disabled!'
            embed.description = f'{ctx.command.qualified_name} has been disabled.'
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingAnyRole):
            roles = ', '.join(error.missing_roles)
            embed.title = 'Missing Roles!'
            embed.description = f'Error: You must have any of the following roles to run this command: {roles}'
            return await ctx.send(embed)

        elif isinstance(error, commands.EmojiNotFound):
            return await ctx.send('I could not find the emoji that you provided. Either I do not have access to it, '
                                  'or it is a default emoji.')

        elif isinstance(error, commands.CheckFailure):
            embed.title = 'Permission Error!'
            msg = str(error) or 'You are not allowed to run this command.'
            embed.description = f'Error: {msg}'
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.title = 'Missing Argument!'
            embed.description = 'Error: ' + str(error) or "An error has occurred. Please contact the developer."
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
            embed.title = 'Invalid Argument!'
            embed.description = 'Error: ' + str(error) or "Unknown Bad Argument"
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.ArgumentParsingError) or isinstance(error, commands.TooManyArguments):
            embed.title = 'Invalid Argument(s)!'
            embed.description = 'Error: ' + str(error) or "Unknown Argument Parsing Error"
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            embed.title = 'Command on Cooldown!'
            cooldown = pendulum.duration(seconds=int(error.retry_after))
            embed.description = f'`{ctx.prefix}{ctx.command.qualified_name}`' \
                                f' is on cooldown for {cooldown.in_words()}'
            return await ctx.send(embed=embed)

        elif isinstance(error, discord.Forbidden):
            embed.title = 'Forbidden!'
            embed.description = 'Error: ' + str(error) or "Not allowed to perform this action."
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            self.log_error(error, context=ctx)
            embed.title = 'Unknown Error!'
            embed.description = 'An unknown error has occurred! A notification has been sent to the bot developer.'
            embed.add_field(name='Error Type', value=f'{type(error)}')
            log.error('Ignoring exception in command {}:'.format(ctx.command))
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
