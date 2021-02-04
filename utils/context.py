from discord.ext import commands
import discord
import asyncio
from cogs.rpg.models.character import Character
from utils.functions import create_default_embed, try_delete


class PoddoContext(commands.Context):
    @property
    def guild_id(self):
        return getattr(self.guild, 'id', None)

    async def get_character(self, db_name='rpg-characters-db'):
        """
        Returns the Character for the author of the message. Returns None if the character is not found.
        :param db_name: The name of the database to use (Optional!)
        :return: The Character
        :rtype: Character
        """

        data = await self.bot.mdb[db_name].find_one({'owner_id': self.author.id})
        if data is None:
            return None
        return Character.from_dict(data)

    async def prompt(self, title: str, description: str, timeout=30, sendable=None) -> str:
        """
        Prompts the Context author for a question, and returns the result. Returns None if they do not respond.
        :param str title: The title of the prompt
        :param str description: The description of the prompt
        :param int timeout:
        :param discord.Messagable sendable: Where to send the message. (Optional, defaults to context channel.)
        :return: The response, or None
        :rtype: str or None
        """
        embed = create_default_embed(self)
        embed.title = title or 'Question Prompt'

        if not description:
            raise Exception('Missing required argument Description on prompt.')
        embed.description = description

        if sendable:
            question = await sendable.send(embed=embed)
        else:
            question = await self.channel.send(embed=embed)

        def check(msg: discord.Message):
            return msg.author.id == self.author.id and msg.channel.id == self.channel.id

        try:
            result = await self.bot.wait_for('message', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            return None

        content = result.content
        await try_delete(question)
        await try_delete(result)

        return content or None
