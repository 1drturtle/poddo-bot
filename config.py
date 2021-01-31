import os

PREFIX = os.getenv('DISCORD_BOT_PREFIX', '=')
DEV_ID = int(os.getenv('DEV_ID', '175386962364989440'))
TOKEN = os.getenv('DISCORD_BOT_TOKEN', None)
MONGO_URL = os.getenv('DISCORD_MONGO_URL', '')
MONGO_DB = os.getenv('MONGO_DB', 'testpoddodb')
DEFAULT_STATUS = os.getenv('DISCORD_STATUS', f'{PREFIX}help for help.')

# Version
VERSION = os.getenv('VERSION', 'testing')

# Error Reporting
SENTRY_URL = os.getenv('SENTRY_URL', None)
ENVIRONMENT = os.getenv('ENVIRONMENT', 'testing')
