import discord
from datetime import datetime
__all__ = ('try_delete', 'create_default_embed', 'yes_or_no')


async def try_delete(message):
    try:
        await message.delete()
    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
        pass


def create_default_embed(ctx, **options) -> discord.Embed:
    embed = discord.Embed(color=discord.Color(int('0x2F3136', base=16)), **options)
    bot = ctx.bot
    embed.set_author(name=ctx.message.author.display_name, icon_url=str(ctx.message.author.avatar_url))
    embed.set_footer(text=bot.user.name, icon_url=str(bot.user.avatar_url))
    embed.timestamp = datetime.utcnow()
    return embed


def yes_or_no(content):
    if isinstance(content, bool):
        return content
    if str(content).lower() in ['yes', 'y', 'true', 'on', '1']:
        return True
    if str(content.lower()) in ['no', 'n', 'false', 'off', '0']:
        return False
