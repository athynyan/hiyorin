import os
from discord.ext import commands


class Main(commands.Cog):

    def __init__(self, client):
        self.client = client

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != 'main.py':
                self.client.load_extension(f'cogs.{filename[:-3]}')
        print("Bot is ready.")

    # commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, extension):
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} loaded.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} removed.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} reloaded.')


def setup(client):
    client.add_cog(Main(client))
