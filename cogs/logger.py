from discord.ext import commands
from discord import Message


class DiscordLogger(commands.Cog):
    """Logs events like deleted messages."""
    def __init__(self, bot):
        self.bot = bot
        self.deleted_db = bot.mdb['deleted-message-logs']

    @commands.Cog.listener(name='on_message_delete')
    async def log_message_delete(self, msg: Message):
        """Logs a deleted message to the DB."""

        # Skip if it's a bot
        if msg.author.bot:
            return None

        # create the log
        await self.deleted_db.insert_one({
            'message_sent': msg.created_at,
            'content': msg.clean_content,
            'author_id': msg.author.id
        })


def setup(bot):
    bot.add_cog(DiscordLogger(bot))
