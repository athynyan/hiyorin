import discord
from discord.ext import commands


class Boss:
    def __init__(self):
        self.names = []
        self.health = None


class Round:
    def __init__(self):
        self.boss = [Boss() for _ in range(5)]


class CB(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.IsActiveCB = False
        self.currentRound = 0
        self.currentBoss = 0
        self.rounds = []

    # events
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print('reaction added.')

    # commands
    @commands.command()
    async def start(self, ctx):
        self.IsActiveCB = True
        self.currentRound = 1
        self.currentBoss = 1
        self.rounds = [Round() for _ in range(100)]
        await ctx.send('Clan Battle has started.')

    @commands.command()
    async def end(self, ctx):
        self.IsActiveCB = False
        self.rounds.clear()
        await ctx.send('Clan Battle has ended.')

    @commands.command()
    async def queue(self, ctx, round=None):
        if self.IsActiveCB:
            if round is None:
                round = self.currentRound
            if int(round) < 0 or int(round) > 100:
                await ctx.send('no')
                return

            embed = discord.Embed(title='Queue',
                                  description=f'Round {int(round)}',
                                  color=0x06ade5)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/286838882392080384/769995627484151818"
                                    "/1580219100588.gif")

            for i in range(self.currentBoss - 1, 5):
                if len(self.rounds[int(round) - 1].boss[i].names):
                    embed.add_field(name=f'B{i + 1}',
                                    value=', '.join(self.rounds[int(round) - 1].boss[i].names),
                                    inline=False)
                else:
                    embed.add_field(name=f'B{i + 1}',
                                    value='???',
                                    inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Clan Battle hasn't started.")

    @commands.command()
    async def add(self, ctx, round, boss):
        if self.IsActiveCB:
            self.rounds[int(round) - 1].boss[int(boss) - 1].names.append(ctx.message.author.mention)
            await ctx.send(f'{ctx.message.author.mention} was added to B{boss} in round {round}.')
        else:
            await ctx.send(f"Clan Battle hasn't started.")

    @commands.command()
    async def remove(self, ctx, round, boss):
        if self.IsActiveCB:
            self.rounds[int(round) - 1].boss[int(boss) - 1].names.remove(ctx.message.author.mention)
            await ctx.send(f'{ctx.message.author.mention} was removed from B{boss} in round {round}.')
        else:
            await ctx.send(f"Clan Battle hasn't started.")

    @commands.command()
    async def next(self, ctx):
        if self.IsActiveCB:
            if self.currentBoss > 5:
                self.currentRound += 1
                self.currentBoss = 1
            else:
                self.currentBoss += 1
            await ctx.send(f'Proceeding to B{self.currentBoss}.')
        else:
            await ctx.send(f"Clan Battle hasn't started.")


def setup(client):
    client.add_cog(CB(client))
