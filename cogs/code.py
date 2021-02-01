from discord.ext import commands

# commands
# `bin` - upload code from file or input to bin


class Code(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Code(bot))
