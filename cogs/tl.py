from discord.ext import commands
from modules.helpers.tl import make_tl_embed


class Tl(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def tl(self, ctx, *text):
        await ctx.message.channel.send(embed=make_tl_embed(text))
        await ctx.message.delete()


def setup(client):
    client.add_cog(Tl(client))