import datetime
import logging
import sys

import discord
import motor.motor_asyncio
from discord.ext import commands

import config
from utils.context import PoddoContext
from utils.functions import *

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[{asctime}] [{levelname}] | {name}: {message}', style='{'))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Make discord logs a bit quieter
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.client').setLevel(logging.WARNING)

log = logging.getLogger(__name__)

COGS = {
    'jishaku', 'cogs.admin', 'cogs.utils', 'cogs.code', 'cogs.error_handling',
    'cogs.rpg.cog',
    'cogs.help'
}


async def get_prefix(client, message):
    if not message.guild:
        return commands.when_mentioned_or(config.PREFIX)(client, message)
    guild_id = str(message.guild.id)
    if guild_id in client.prefixes:
        # if we already have a cached prefix, use that
        prefix = client.prefixes.get(guild_id, config.PREFIX)
    else:
        # db search
        result = await client.mdb['prefixes'].find_one({'guild_id': guild_id})
        if result is not None:
            prefix = result.get('prefix', config.PREFIX)
        else:
            prefix = config.PREFIX
        # cache prefix
        client.prefixes[guild_id] = prefix
    return commands.when_mentioned_or(prefix)(client, message)


class PoddoBot(commands.Bot):
    def __init__(self, command_prefix=get_prefix, desc='', **options):
        self.launch_time = datetime.datetime.utcnow()

        self.ready_time = None
        self._dev_id = config.DEV_ID
        self.environment = config.ENVIRONMENT

        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
        self.mdb = self.mongo_client[config.MONGO_DB]

        self.sentry_url = config.SENTRY_URL
        self.prefixes = dict()

        super(PoddoBot, self).__init__(command_prefix, description=desc, **options)

    @property
    def dev_id(self):
        return self._dev_id

    @property
    def uptime(self):
        return datetime.datetime.utcnow() - self.launch_time

    # ---- Overrides ----
    async def get_context(self, message, *, cls=PoddoContext):
        return await super().get_context(message, cls=cls)


intents = discord.Intents(guilds=True, members=True, messages=True, reactions=True)

description = 'Dr Turtle\'s bot.'

bot = PoddoBot(desc=description, intents=intents, allowed_mentions=discord.AllowedMentions.none())


@bot.event
async def on_ready():

    bot.ready_time = datetime.datetime.utcnow()

    ready_message = f'\n{"-"*25}\n' \
                    f'Bot Ready!\n' \
                    f'Logged in as {bot.user.name} (ID: {bot.user.id})\n' \
                    f'Current Prefix: {config.PREFIX}\n' \
                    f'{"-"*25}'
    log.info(ready_message)


@bot.event
async def on_message(message):
    if message.author.bot:
        return None

    if not bot.is_ready():
        return None

    context = await bot.get_context(message)
    if context.command is not None:
        return await bot.invoke(context)


@bot.event
async def on_command(ctx):
    if ctx.command.name in ['py', 'pyi', 'sh']:
        return

    await try_delete(ctx.message)


@bot.event
async def on_guild_join(joined):
    # Check to make sure we aren't approaching guild limit.
    if len(bot.guilds) > 90:
        if joined.system_channel:
            await joined.system_channel.send('Until I am verified, I cannot join any more servers. '
                                             'Please contact my developer if you see this message.')
        await joined.leave()


for cog in COGS:
    bot.load_extension(cog)

if __name__ == '__main__':
    bot.run(config.TOKEN)
