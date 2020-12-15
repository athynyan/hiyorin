from modules.cb.queue import Queue
from modules.cb.rounds import Round
import discord
from discord.ext import commands


class CB(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = None
        self.activeChannel = None
        self.activeMessageList = None
        self.isActiveCB = False
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.channel.id == self.activeChannel and not user.bot:
            bossNum, roundNum = self.add(user, reaction.emoji, reaction.message.id)
            newEmbed = makeEmbed(self.queue.rounds[roundNum], self.queue.currentRound + roundNum)

            await reaction.message.edit(embed=newEmbed)
            print(f'reaction added, message: {reaction.message.id}, user: {user.id}, emoji: {reaction.emoji}')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = await self.client.fetch_user(payload.user_id)
        msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if payload.channel_id == self.activeChannel and not user.bot:
            bossNum, roundNum = self.remove(user, payload.emoji, payload.message_id)
            newEmbed = makeEmbed(self.queue.rounds[roundNum], self.queue.currentRound + roundNum)

            await msg.edit(embed=newEmbed)
            print(f'reaction removed, message: {msg.id}, user: {user.id}, emoji: {payload.emoji}')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def start(self, ctx):
        if not self.isActiveCB:
            self.queue = Queue()
            self.queue.currentBoss = 1
            self.queue.currentRound = 1
            self.isActiveCB = True
            self.activeChannel = ctx.message.channel.id
            await ctx.send(f'CB STARTED.')

            embedList = []
            roundNum = 0
            for round in self.queue.rounds:
                embedList.append(makeEmbed(round, self.queue.currentRound + roundNum))
                roundNum += 1

            for i in range(3):
                message = await ctx.send(embed=embedList[i])
                self.queue.rounds[i].messageId = message.id
                for emoji in self.emojis:
                    await message.add_reaction(emoji)
        else:
            await ctx.send('CB ALREADY STARTED.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def end(self, ctx):
        self.queue = None
        self.isActiveCB = False
        await ctx.send('CB ENDED.')

    @commands.command()
    async def kill(self, ctx):
        if isActiveCB:
            if self.queue.currentBoss > 4:
                self.queue.currentRound += 1
                self.queue.currentBoss = 1
                await ctx.send(f'Proceeding to round {self.queue.currentRound}.')

                newRound = Round()
                newEmbed = makeEmbed(newRound, self.queue.currentRound + 2)
                channel = self.client.get_channel(self.activeChannel)
                message = await channel.send(embed=newEmbed)
                for emoji in self.emojis:
                    await message.add_reaction(emoji)
                newRound.messageId = message.id

                self.queue.rounds.pop(0)
                self.queue.rounds.append(newRound)
            else:
                self.queue.currentBoss += 1

            await ctx.send(f'B{self.queue.currentBoss} is up.')

            mentions = self.queue.rounds[0].bosses[self.queue.currentBoss-1].names
            if mentions:
                await ctx.send(', '.join(mentions))

    def add(self, user, emoji, messageId):
        bossNum = 0
        roundNum = 0
        for i in range(len(self.queue.rounds)):
            round = self.queue.rounds[i]
            if round.messageId == messageId:
                for boss in range(5):
                    if emoji == self.emojis[boss]:
                        round.bosses[boss].names.append(f'<@{user.id}>')
                        bossNum = boss
                roundNum = i

        return bossNum, roundNum

    def remove(self, user, emoji, messageId):
        bossNum = 0
        roundNum = 0
        for i in range(len(self.queue.rounds)):
            round = self.queue.rounds[i]
            if round.messageId == messageId:
                for boss in range(5):
                    if emoji == self.emojis[boss]:
                        round.bosses[boss].names.remove(f'<@{user.id}>')
                        bossNum = boss
                roundNum = i

        return bossNum, roundNum

def makeEmbed(round, roundNum):
    bossNum = 0
    embed = discord.Embed(title=f'Round {roundNum}',
                          color=0x06ade5)
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/286838882392080384/769995627484151818"
                            "/1580219100588.gif")
    for boss in round.bosses:
        if boss.names:
            embed.add_field(name=f'B{bossNum + 1}',
                            value=', '.join(boss.names),
                            inline=False)
        else:
            embed.add_field(name=f'B{bossNum + 1}',
                            value='???',
                            inline=False)
        bossNum += 1
    return embed


def setup(client):
    client.add_cog(CB(client))
