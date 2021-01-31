from discord.ext import commands
import asyncio
import discord


class PoddoContext(commands.Context):
    @property
    def guild_id(self):
        return getattr(self.guild, 'id', None)
