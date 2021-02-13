import logging
import sys

import discord

import config
from bot import PoddoBot, COGS

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[{asctime}] [{levelname}] | {name}: {message}', style='{'))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Make discord logs a bit quieter
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.client').setLevel(logging.WARNING)

log = logging.getLogger(__name__)

intents = discord.Intents(guilds=True, members=True, messages=True, reactions=True)

description = 'Dr Turtle\'s bot.'

bot = PoddoBot(desc=description, intents=intents, allowed_mentions=discord.AllowedMentions.none())

for cog in COGS:
    bot.load_extension(cog)

if __name__ == '__main__':
    bot.run(config.TOKEN)
