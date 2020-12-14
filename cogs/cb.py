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
        self.currentQueueMessage = None
        self.contextUser = None
        self.contextRound = None
        self.activeCbChannel = None
        self.currentRound = None
        self.currentBoss = None
        self.rounds = []
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

    # events
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.id == self.currentQueueMessage and user.id == self.contextUser and reaction.count == 2:
            for boss in range(5):
                if reaction.emoji == self.emojis[boss]:
                    self.rounds[self.contextRound-1].boss[boss].names.append(f'<@{user.id}>')
                    await reaction.message.channel.send(f'<@{user.id}> was added to B{boss+1} '
                                                        f'in round {self.contextRound}')

        print(f'reaction added, message: {reaction.message.id}, user: {user.id}')

    # commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def start(self, ctx):
        self.IsActiveCB = True
        self.currentRound = 1
        self.currentBoss = 1
        self.rounds = [Round() for _ in range(100)]
        self.activeCbChannel = ctx.message.channel.id
        await ctx.send('Clan Battle has started.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def end(self, ctx):
        self.IsActiveCB = False
        self.rounds.clear()
        await ctx.send('Clan Battle has ended.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setr(self, ctx, round):
        self.currentRound = round
        await ctx.send(f'Current round set to {round}.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setb(self, ctx, boss):
        self.currentBoss = boss
        await ctx.send(f'Current boss set to {boss}.')

    @commands.command()
    async def queue(self, ctx, round=None):
        if self.IsActiveCB and self.activeCbChannel == ctx.message.channel.id:
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

            message = await ctx.send(embed=embed)
            self.currentQueueMessage = message.id
            self.contextUser = ctx.message.author.id
            self.contextRound = round
            for emoji in self.emojis:
                await message.add_reaction(emoji)
        else:
            await ctx.send(f"Clan Battle hasn't started.")

    @commands.command()
    async def add(self, ctx, round, boss):
        if self.IsActiveCB and self.activeCbChannel == ctx.message.channel.id:
            self.rounds[int(round) - 1].boss[int(boss) - 1].names.append(ctx.message.author.mention)
            await ctx.send(f'{ctx.message.author.mention} was added to B{boss} in round {round}.')
        else:
            if self.activeCbChannel != ctx.message.channel.id:
                await ctx.send(f'This is not the channel for clan battle!')
            else:
                await ctx.send(f"Clan Battle hasn't started.")

    @commands.command()
    async def remove(self, ctx, round, boss):
        if self.IsActiveCB and self.activeCbChannel == ctx.message.channel.id:
            self.rounds[int(round) - 1].boss[int(boss) - 1].names.remove(ctx.message.author.mention)
            await ctx.send(f'{ctx.message.author.mention} was removed from B{boss} in round {round}.')
        else:
            if self.activeCbChannel != ctx.message.channel.id:
                await ctx.send(f'This is not the channel for clan battle.')
            else:
                await ctx.send(f"Clan Battle hasn't started.")

    @commands.command()
    async def next(self, ctx):
        if self.IsActiveCB:
            if self.currentBoss > 4:
                self.currentRound += 1
                self.currentBoss = 1
                await ctx.send(f'Proceeding to round {self.currentRound}')
            else:
                self.currentBoss += 1

            queuedUsers = self.rounds[self.currentRound - 1].boss[self.currentBoss - 1].names
            await ctx.send(f'B{self.currentBoss} is up.')
            if queuedUsers:
                await ctx.send(' ,'.join(queuedUsers))
        else:
            await ctx.send(f"Clan Battle hasn't started.")


def setup(client):
    client.add_cog(CB(client))
