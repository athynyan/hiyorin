import discord
import pytz
from models.cb.queue import Queue
from models.cb.rounds import Round
from discord.ext import commands, tasks
from datetime import datetime
from utils.sql import Sql
from utils.updateTemplate import queueTemplate, roundTemplate

class CB(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = None
        self.activeDate = None
        self.activeChannel = None
        self.activeRoundCounter = None
        self.killChannel = None
        self.isActiveCB = False
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        self.qtemp = None
        self.rtemps = []
        self.db = None

    # events
    @commands.Cog.listener('on_ready')
    async def load_data(self):
        self.db = Sql()
        self.qtemp = self.db.getData('Q')

        self.isActiveCB = self.qtemp.active
        self.activeDate = self.qtemp.date
        self.activeChannel = self.qtemp.channel
        self.activeRoundCounter = self.qtemp.counter
        self.killChannel = self.qtemp.kill
        print('Data loaded.')

        self.updateDb.start()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.updateQueueTable(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.updateQueueTable(payload, False)

    # tasks
    @tasks.loop(minutes=60.0)
    async def updateDb(self):
        self.qtemp.active = self.isActiveCB
        self.qtemp.date = self.activeDate
        self.qtemp.channel = self.activeChannel
        self.qtemp.counter = self.activeRoundCounter
        self.qtemp.kill = self.killChannel

        if self.queue:
            self.qtemp.currentTier = self.queue.currentTier
            self.qtemp.currentRound = self.queue.currentRound
            self.qtemp.currentBoss = self.queue.currentBoss

            if self.queue.rounds:
                for round in self.queue.rounds:
                    if self.rtemps:
                        self.rtemps.clear()
                    self.rtemps.append(roundTemplate(round.messageId))

        self.db.update(self.qtemp)
        if self.rtemp:
            self.db.update(self.rtemps)

    @tasks.loop(seconds=1.0, count=1800)
    async def syncWithClock(self):
        currentTime = datetime.now(pytz.timezone('Japan'))
        minutes = currentTime.strftime('%M')
        if minutes == '00' or minutes == '30':
            self.groupPing.start()

    @tasks.loop(minutes=30.0)
    async def groupPing(self):
        currentTime = datetime.now(pytz.timezone('Japan'))
        hour = currentTime.strftime('%H')
        minute = currentTime.strftime('%M')
        if self.killChannel is not None:
            channel = self.client.get_channel(self.killChannel)
            role = None
            if hour == '05' and minute == '00':
                role = discord.utils.get(channel.guild.roles, name='Group 1')
            if hour == '08' and minute == '30':
                role = discord.utils.get(channel.guild.roles, name='Group 2')
            if hour == '13' and minute == '00':
                role = discord.utils.get(channel.guild.roles, name='Group 3')
            if hour == '19' and minute == '00':
                role = discord.utils.get(channel.guild.roles, name='Group 4')

            await channel.send(role.mention)
            await channel.send('https://cdn.discordapp.com/attachments/163948097330741248/759655070295654430/images_-_2020-08-28T104748.758.jpg')

    @groupPing.before_loop
    async def beforeGroupPing(self):
        self.syncWithClock.cancel()

    # commands
    @commands.command()
    @commands.has_role('Labyrinth Crepe Shop')
    async def start(self, ctx):
        if not self.isActiveCB:
            await ctx.message.channel.purge(limit=10)
            self.queue = Queue()
            self.queue.currentBoss = 1
            self.queue.currentRound = 1
            self.queue.updateTier()
            self.isActiveCB = True
            self.activeChannel = ctx.message.channel.id
            self.syncWithClock.start()
            today = datetime.now()
            self.activeDate = today.strftime('%B %Y')
            queueCounter = makeCounterEmbed(self.queue.currentRound, self.queue.currentBoss, self.queue.currentTier,
                                            self.activeDate)
            message = await ctx.send(embed=queueCounter)
            self.activeRoundCounter = message.id

            embedList = []
            roundNum = 0
            for round in self.queue.rounds:
                embedList.append(makeQueueEmbed(round, self.queue.currentRound + roundNum))
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
        for round in self.queue.rounds:
            message = await self.client.get_channel(self.activeChannel).fetch_message(
                round.messageId)
            await message.delete()
        self.queue = None
        self.isActiveCB = False
        self.syncWithClock.cancel()
        self.groupPing.cancel()
        await ctx.message.channel.purge(limit=10)

    @commands.command()
    @commands.check_any(commands.has_role('Labyrinth Crepe Shop'), commands.has_role('Shuujin'))
    @commands.cooldown(1, 15)
    async def kill(self, ctx): # TODO: change queue table generation after round 45
        if self.isActiveCB:
            if self.killChannel is None:
                self.killChannel = ctx.message.channel.id

            if self.queue.currentBoss > 4:
                self.queue.currentRound += 1
                self.queue.currentBoss = 1
                await ctx.send(f'Proceeding to round {self.queue.currentRound}.')

                if self.queue.currentRound <= 43:
                    # add next round
                    newRound = Round()
                    newEmbed = makeQueueEmbed(newRound, self.queue.currentRound + 2)
                    channel = self.client.get_channel(self.activeChannel)
                    message = await channel.send(embed=newEmbed)
                    for emoji in self.emojis:
                        await message.add_reaction(emoji)
                    newRound.messageId = message.id
                    self.queue.rounds.append(newRound)

                # remove oldest round embed
                message = await self.client.get_channel(self.activeChannel).fetch_message(
                    self.queue.rounds[0].messageId)
                if message:
                    await message.delete()
                    self.queue.rounds.pop(0)

            else:
                # increment boss counter by 1
                self.queue.currentBoss += 1

            self.queue.updateTier()
            await ctx.send(f'B{self.queue.currentBoss} is up.')
            if self.queue.currentRound > 45:
                role = discord.utils.get(channel.guild.roles, name=f'Tier 5 Boss {self.queue.currentBoss}')
                await ctx.send(role.mention)

            # edit current boss and round message
            newCounterEmbed = makeCounterEmbed(self.queue.currentRound, self.queue.currentBoss, self.queue.currentTier,
                                               self.activeDate)
            message = await self.client.get_channel(self.activeChannel).fetch_message(self.activeRoundCounter)
            await message.edit(embed=newCounterEmbed)

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

                if self.queue.currentRound <= 43:
                    # add next round
                    newRound = Round()
                    newEmbed = makeQueueEmbed(newRound, self.queue.currentRound + 2)
                    channel = self.client.get_channel(self.activeChannel)
                    message = await channel.send(embed=newEmbed)
                    for emoji in self.emojis:
                        await message.add_reaction(emoji)
                    newRound.messageId = message.id
                    self.queue.rounds.append(newRound)

                # remove oldest round embed
                message = await self.client.get_channel(self.activeChannel).fetch_message(
                    self.queue.rounds[0].messageId)
                if message:
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
                    embedList.append(makeQueueEmbed(round, self.queue.currentRound + roundNum))
                    roundNum += 1
                channel = self.client.get_channel(self.activeChannel)
                for i in range(3):
                    message = await channel.send(embed=embedList[i])
                    self.queue.rounds[i].messageId = message.id
                    for emoji in self.emojis:
                        await message.add_reaction(emoji)

            self.queue.updateTier()
            await ctx.send(f'B{self.queue.currentBoss} is up.')

            # edit current boss and round message
            newCounterEmbed = makeCounterEmbed(self.queue.currentRound, self.queue.currentBoss, self.queue.currentTier,
                                               self.activeDate)
            message = await self.client.get_channel(self.activeChannel).fetch_message(self.activeRoundCounter)
            await message.edit(embed=newCounterEmbed)

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
        newEmbed = makeQueueEmbed(self.queue.rounds[int(messageNum) - 1], self.queue.currentRound + int(messageNum) - 1)
        message = await self.client.get_channel(self.activeChannel).fetch_message(
            self.queue.rounds[int(messageNum) - 1].messageId)
        await message.edit(embed=newEmbed)

    @commands.command()
    async def ovf(self, ctx, damage, remainingHp):
        formattedDamage = await formatNumber(damage)
        formattedHp = await formatNumber(remainingHp)
        overflowTime = ((formattedDamage - formattedHp) / formattedDamage) * 90 + 20
        if overflowTime < 0:
            overflowTime = 0
        if overflowTime > 90:
            overflowTime = 90
        await ctx.send(f'{round(overflowTime, 2)}s')

    # class methods
    def updateQueue(self, user, emoji, messageId, add=True):
        roundNum = 0
        for i in range(len(self.queue.rounds)):
            round = self.queue.rounds[i]
            if round.messageId == messageId:
                for boss in range(5):
                    if str(emoji) == self.emojis[boss]:
                        if add and user.mention not in round.bosses[boss].names:
                            round.bosses[boss].names.append(user.mention)
                        else:
                            round.bosses[boss].names.remove(user.mention)
                roundNum = i

        return roundNum

    async def updateQueueTable(self, payload, add=True):
        msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        user = await msg.guild.fetch_member(payload.user_id)
        expectedRole = discord.utils.get(msg.guild.roles, name='Shuujin')
        if payload.channel_id == self.activeChannel and not user.bot and hasRole(expectedRole, user):
            if add:
                roundNum = self.updateQueue(user, payload.emoji, payload.message_id)
            else:
                roundNum = self.updateQueue(user, payload.emoji, payload.message_id, False)
            newEmbed = makeQueueEmbed(self.queue.rounds[roundNum], self.queue.currentRound + roundNum)

            await msg.edit(embed=newEmbed)
            print(f'reaction caught, message: {msg.id}, user: {user.id}, emoji: {payload.emoji}')


# global functions
def hasRole(expectedRole, user):
    for role in user.roles:
        if role == expectedRole:
            return True
    return False


async def formatNumber(string):
    if string[-1] == 'M' or string[-1] == 'm':
        return float(string[:-1]) * 1000000
    elif string[-1] == 'K' or string[-1] == 'k':
        return float(string[:-1]) * 1000
    else:
        return float(string)


def makeQueueEmbed(round, roundNum):
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


def makeCounterEmbed(roundNum, bossNum, tierNum, thisDate):
    embed = discord.Embed(color=0x6d2c2c)
    embed.add_field(name=f"CB {thisDate}", value=f'\u200b', inline=False)
    embed.add_field(name="Current Round", value=roundNum, inline=True)
    embed.add_field(name="Current Boss", value=bossNum, inline=True)
    embed.add_field(name="Current Tier", value=tierNum, inline=True)
    return embed


def setup(client):
    client.add_cog(CB(client))
