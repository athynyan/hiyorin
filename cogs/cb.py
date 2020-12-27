from models.cb.queue import Queue
from models.cb.rounds import Round
import discord
from discord.ext import commands


class CB(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = None
        self.activeChannel = None
        self.activeRoundCounter = None
        self.isActiveCB = False
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        expectedRole = discord.utils.get(reaction.message.guild.roles, name='Shuujin')
        if reaction.message.channel.id == self.activeChannel and not user.bot and hasRole(expectedRole, user):
            roundNum = self.add(user, reaction.emoji, reaction.message.id)
            newEmbed = makeEmbed(self.queue.rounds[roundNum], self.queue.currentRound + roundNum)

            await reaction.message.edit(embed=newEmbed)
            print(f'reaction added, message: {reaction.message.id}, user: {user.id}, emoji: {reaction.emoji}')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = await self.client.fetch_user(payload.user_id)
        msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if payload.channel_id == self.activeChannel and not user.bot:
            roundNum = self.remove(user, payload.emoji, payload.message_id)
            newEmbed = makeEmbed(self.queue.rounds[roundNum], self.queue.currentRound + roundNum)

            await msg.edit(embed=newEmbed)
            print(f'reaction removed, message: {msg.id}, user: {user.id}, emoji: {payload.emoji}')

    @commands.command()
    @commands.has_role('Labyrinth Crepe Shop')
    async def start(self, ctx):
        if not self.isActiveCB:
            await ctx.message.channel.purge(limit=10)
            self.queue = Queue()
            self.queue.currentBoss = 1
            self.queue.currentRound = 1
            self.isActiveCB = True
            self.activeChannel = ctx.message.channel.id
            message = await ctx.send(f'=== CURRENT ROUND: {self.queue.currentRound} ===\n'
                                     f'=== CURRENT BOSS: {self.queue.currentBoss} ===')
            self.activeRoundCounter = message.id

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
    @commands.has_role('Labyrinth Crepe Shop')
    async def end(self, ctx):
        self.queue = None
        self.isActiveCB = False
        await ctx.message.channel.purge(limit=10)

    @commands.command()
    @commands.check_any(commands.has_role('Labyrinth Crepe Shop'), commands.has_role('Shuujin'))
    @commands.cooldown(1,15)
    async def kill(self, ctx):
        if self.isActiveCB:
            if self.queue.currentBoss > 4:
                self.queue.currentRound += 1
                self.queue.currentBoss = 1
                await ctx.send(f'Proceeding to round {self.queue.currentRound}.')

                #add next round
                newRound = Round()
                newEmbed = makeEmbed(newRound, self.queue.currentRound + 2)
                channel = self.client.get_channel(self.activeChannel)
                message = await channel.send(embed=newEmbed)
                for emoji in self.emojis:
                    await message.add_reaction(emoji)
                newRound.messageId = message.id
                self.queue.rounds.append(newRound)

                # remove oldest round embed
                message = await self.client.get_channel(self.activeChannel).fetch_message(self.queue.rounds[0].messageId)
                await message.delete()
                self.queue.rounds.pop(0)

            else:
                # increment boss counter by 1
                self.queue.currentBoss += 1

            await ctx.send(f'B{self.queue.currentBoss} is up.')

            # edit current boss and round message
            message = await self.client.get_channel(self.activeChannel).fetch_message(self.activeRoundCounter)
            await message.edit(content=str(f'=== CURRENT ROUND: {self.queue.currentRound} ===\n'
                                           f'=== CURRENT BOSS: {self.queue.currentBoss} ==='))

            # mention members queued up for the next
            mentions = self.queue.rounds[0].bosses[self.queue.currentBoss - 1].names
            if mentions:
                await ctx.send(', '.join(mentions))

    @commands.command()
    @commands.has_role('Labyrinth Crepe Shop')
    async def next(self, ctx, round=0):
        if self.isActiveCB:
            if round == 0:
                self.queue.currentRound += 1
                self.queue.currentBoss = 1
                await ctx.send(f'Proceeding to round {self.queue.currentRound}.')

                # add next round
                newRound = Round()
                newEmbed = makeEmbed(newRound, self.queue.currentRound + 2)
                channel = self.client.get_channel(self.activeChannel)
                message = await channel.send(embed=newEmbed)
                for emoji in self.emojis:
                    await message.add_reaction(emoji)
                newRound.messageId = message.id
                self.queue.rounds.append(newRound)

                # remove oldest round embed
                message = await self.client.get_channel(self.activeChannel).fetch_message(self.queue.rounds[0].messageId)
                await message.delete()
                self.queue.rounds.pop(0)
            else:
                self.queue.currentRound = round
                self.queue.currentBoss = 1
                await ctx.send(f'Proceeding to round {self.queue.currentRound}.')

                embedList = []
                roundNum = 0
                for round in self.queue.rounds:
                    message = await self.client.get_channel(self.activeChannel).fetch_message(
                        round.messageId)
                    await message.delete()
                    embedList.append(makeEmbed(round, self.queue.currentRound + roundNum))
                    roundNum += 1
                channel = self.client.get_channel(self.activeChannel)
                for i in range(3):
                    message = await channel.send(embed=embedList[i])
                    self.queue.rounds[i].messageId = message.id
                    for emoji in self.emojis:
                        await message.add_reaction(emoji)

            await ctx.send(f'B{self.queue.currentBoss} is up.')

            # edit current boss and round message
            message = await self.client.get_channel(self.activeChannel).fetch_message(self.activeRoundCounter)
            await message.edit(content=str(f'=== CURRENT ROUND: {self.queue.currentRound} ===\n'
                                           f'=== CURRENT BOSS: {self.queue.currentBoss} ==='))

            # mention members queued up for the next
            mentions = self.queue.rounds[0].bosses[self.queue.currentBoss - 1].names
            if mentions:
                await ctx.send(', '.join(mentions))

    @commands.command()
    @commands.has_role('Labyrinth Crepe Shop')
    async def rm(self, ctx, messageNum, bossNum, user):
        print(f'{messageNum}, {bossNum}, {user}')
        nameList = self.queue.rounds[int(messageNum) - 1].bosses[int(bossNum) - 1].names
        if user in nameList:
            nameList.remove(user)

        # update embed
        newEmbed = makeEmbed(self.queue.rounds[int(messageNum) - 1], self.queue.currentRound + int(messageNum) - 1)
        message = await self.client.get_channel(self.activeChannel).fetch_message(self.queue.rounds[int(messageNum) - 1].messageId)
        await message.edit(embed=newEmbed)


    def add(self, user, emoji, messageId):
        bossNum = 0
        roundNum = 0
        for i in range(len(self.queue.rounds)):
            round = self.queue.rounds[i]
            if round.messageId == messageId:
                for boss in range(5):
                    if emoji == self.emojis[boss] and f'<@!{user.id}>' not in round.bosses[boss].names:
                        round.bosses[boss].names.append(f'<@!{user.id}>')
                        bossNum = boss
                roundNum = i

        return roundNum

    def remove(self, user, emoji, messageId):
        # TODO: fix this shit
        bossNum = 0
        roundNum = 0
        for i in range(len(self.queue.rounds)):
            round = self.queue.rounds[i]
            if round.messageId == messageId:
                for boss in range(5):
                    if emoji == self.emojis[boss] and f'<@!{user.id}>' in round.bosses[boss].names:
                        round.bosses[boss].names.remove(f'<@!{user.id}>')
                        bossNum = boss
                roundNum = i

        return roundNum

def hasRole(expectedRole, user):
    for role in user.roles:
        if role == expectedRole:
            return True
    return False

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
