import os

import discord.ext.commands.errors
from dotenv import load_dotenv
from discord.ext import commands

# load_dotenv()
client = commands.Bot(command_prefix=os.getenv('PREFIX'))


@client.event
async def on_ready():
    print('Ready')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(os.getenv('TOKEN'))
