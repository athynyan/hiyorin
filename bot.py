import os
from discord.ext import commands

bot = commands.Bot(command_prefix='?')
bot.load_extension(f'cogs.main')

bot.run('NzcyMjEyNDc2NjI0MjQwNjkw.X53Y6Q.zjIHSxoc5PYIxOJmNjljGYWJ2dU')
