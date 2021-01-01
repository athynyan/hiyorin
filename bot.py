import os
from discord.ext import commands

bot = commands.Bot(command_prefix=os.environ.get("PREFIX"))
bot.load_extension(f'cogs.main')

bot.run(os.environ.get("TOKEN"))
