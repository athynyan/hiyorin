import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
client = commands.Bot(command_prefix=os.getenv('PREFIX'))


@client.event
async def on_ready():
    print('Ready')


@client.command()
async def reload(ctx, module_name):
    if f'{module_name}.py' in os.listdir('./cogs'):
        client.reload_extension(f'cogs.{module_name}')
    await ctx.message.channel.send(f'{module_name} reloaded.')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(os.getenv('TOKEN'))
