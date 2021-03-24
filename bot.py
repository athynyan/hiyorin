import os
import datetime
import discord
from discord.ext import tasks, commands
from pymongo import MongoClient


reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
queue = {}
client = commands.Bot(command_prefix=os.getenv('PREFIX'))


## DISCORD TASKS ##
@tasks.loop(minutes=30.0)
async def update_mongo():
    update_db()


## DISCORD EVENTS ##
@client.event
async def on_ready():
    load_from_db()

    update_mongo.start()
    print('Ready')


@client.event
async def on_raw_reaction_add(payload):
    user = await client.fetch_user(payload.user_id)  # get user from id
    boss_index = get_boss_index(payload.emoji)  # convert emoji to integer

    if user.bot:  # check if reacted user is a bot
        return

    if 'message_id' not in queue: # check if key exists
        return

    # loop to check for matching message
    for message_id in queue['message_id']:
        if payload.message_id == message_id:

            # get message object from channel and message id and it's embed
            msg = await client.get_channel(queue['channel_id']).fetch_message(payload.message_id)
            embed = msg.embeds[0]  # get embed from message

            # check if it's first person reacting
            if embed.fields[boss_index].value == '???':
                embed.set_field_at(boss_index, name=f'B{boss_index + 1}', value=user.mention, inline=False)
            else:
                # store existing values from embed into a temporary list
                mentions = embed.fields[boss_index].value.split(',')

                # check for duplicate users
                if user.mention in mentions:
                    return

                # append user to the embed
                mentions.append(user.mention)
                embed.set_field_at(boss_index, name=f'B{boss_index + 1}', value=','.join(mentions), inline=False)

            # apply changes to the message
            await msg.edit(embed=embed)


@client.event
async def on_raw_reaction_remove(payload):
    user = await client.fetch_user(payload.user_id)  # get user from id
    boss_index = get_boss_index(payload.emoji)  # convert emoji to integer

    if user.bot:  # check if reacted user is a bot
        return

    if 'message_id' not in queue: # check if key exists
        return

    for message_id in queue['message_id']:
        if payload.message_id == message_id:  # check if messages match

            # get message object from channel and message id and it's embed
            msg = await client.get_channel(queue['channel_id']).fetch_message(payload.message_id)
            embed = msg.embeds[0]  # get embed from message

            # check if empty no reactions present
            if embed.fields[boss_index].value == '???':
                return

            # store existing values from embed into a temporary list
            mentions = embed.fields[boss_index].value.split(',')

            # check if user is not in the mention list
            if user.mention not in mentions:
                print('not in mentions')
                return

            # remove user from the embed
            mentions.remove(user.mention)
            if mentions:  # check if list is not empty
                embed.set_field_at(boss_index, name=f'B{boss_index + 1}', value=','.join(mentions), inline=False)
            else:
                embed.set_field_at(boss_index, name=f'B{boss_index + 1}', value='???', inline=False)

            # apply changes to the message
            await msg.edit(embed=embed)


## DISCORD COMMANDS ##
# starts the queue
@client.command()
@commands.check_any(commands.has_role('Labyrinth Crepe Shop'))
async def start(ctx):
    # check if queue is active
    if is_active():
        return

    # initialization of local variables
    message_count = 3  # number of queue tables
    messages = []  # variable to store the message of said tables

    # clear channel messages
    await ctx.message.channel.purge(limit=10)

    # make boss counter
    counter = await ctx.send(embed=make_counter())

    # make queue tables depending on message counts
    for i in range(message_count):
        message = await ctx.send(embed=make_queue_table(i + 1))
        messages.append(message.id)

        # add reactions to the message
        for reaction in reactions:
            await message.add_reaction(reaction)

    # storing data
    queue['active'] = True
    queue['channel_id'] = ctx.message.channel.id
    queue['counter_id'] = counter.id
    queue['message_id'] = messages
    update_db()


# ends queue
@client.command()
@commands.check_any(commands.has_role('Labyrinth Crepe Shop'))
async def end(ctx):
    # check if queue is active
    if not is_active():
        return

    queue.clear()  # clear the queue list
    update_db()
    await ctx.message.channel.purge(limit=10)  # clear messages from the channel


# command to proceed to the next boss
@client.command()
@commands.check_any(commands.has_role('Labyrinth Crepe Shop'), commands.has_role('Shuujin'))
@commands.cooldown(1, 15)
async def kill(ctx):
    # check if queue is active
    if not is_active():
        return

    # get message object of the counter
    channel = client.get_channel(queue['channel_id'])
    msg = await channel.fetch_message(queue['counter_id'])
    embed = msg.embeds[0]

    # new incremented values
    current_round, current_tier, current_boss = increment_current(int(embed.fields[1].value),
                                                                  int(embed.fields[3].value))

    # create new round if current round ended
    if current_round != int(embed.fields[1].value):
        # send notification about new round
        await ctx.send(f'Proceeding to round {current_round}.')

        # create new message and add reactions
        new_message = await channel.send(embed=make_queue_table(current_round + 2))  # TODO: remove hardcode
        for reaction in reactions:
            await new_message.add_reaction(reaction)

        # remove first message
        old_message = await channel.fetch_message(queue['message_id'][0])
        await old_message.delete()

        # save to json
        queue['message_id'].append(new_message.id)
        queue['message_id'].pop(0)
        update_db()

    # editing embed with new values
    embed.set_field_at(1, name='Current Round', value=current_round, inline=True)
    embed.set_field_at(2, name='Current Tier', value=current_tier, inline=True)
    embed.set_field_at(3, name='Current Boss', value=current_boss, inline=False)

    # apply changes to the counter
    await msg.edit(embed=embed)

    # send notification about change in queue
    await ctx.send(f'B{current_boss} up.')

    # get message object of the first queue table
    msg = await client.get_channel(queue['channel_id']).fetch_message(queue['message_id'][0])
    embed = msg.embeds[0]

    # mention everyone who reacted
    mentions = embed.fields[current_boss - 1].value
    if mentions != '???':
        await ctx.send(f'{mentions}')


# command to skip to a different round
@client.command()
@commands.check_any(commands.has_role('Labyrinth Crepe Shop'))
async def next(ctx, round=1):
    # check if queue is active
    if not is_active():
        return

    channel = client.get_channel(queue['channel_id'])
    msg = await channel.fetch_message(queue['counter_id'])
    embed = msg.embeds[0]

    # if skipping 1 round
    if round == 1:
        current_round = int(embed.fields[1].value) + round
        await ctx.send(f'Proceeding to round {current_round}.')

        # change round in the counter
        embed.set_field_at(1, name='Current Round', value=current_round, inline=True)
        await msg.edit(embed=embed)

        # create new message and add reactions
        new_message = await channel.send(embed=make_queue_table(current_round + 2))
        for reaction in reactions:
            await new_message.add_reaction(reaction)

        # remove first message
        old_message = await channel.fetch_message(queue['message_id'][0])
        await old_message.delete()

        # save to json
        queue['message_id'].append(new_message.id)
        queue['message_id'].pop(0)

    # if skipping more than 1 round
    else:
        new_messages = []
        await ctx.send(f'Proceeding to round {round}.')

        # change values in the counter
        embed.set_field_at(1, name='Current Round', value=round, inline=True)
        embed.set_field_at(2, name='Current Tier', value=calculate_tier(round), inline=True)
        embed.set_field_at(3, name='Current Boss', value='1', inline=False)
        await msg.edit(embed=embed)

        # make new queue tables
        for i in range(3):  # TODO: remove hardcode
            # create new message
            channel = client.get_channel(queue['channel_id'])
            new_message = await channel.send(embed=make_queue_table(round + i))
            new_messages.append(new_message.id)  # add to message list

            # add reactions to the new message
            for reaction in reactions:
                await new_message.add_reaction(reaction)

        # clear all previous messages
        for message_id in queue['message_id']:
            old_message = await client.get_channel(queue['channel_id']).fetch_message(message_id)
            await old_message.delete()
        queue['message_id'].clear()  # clear the list with old message ids

        # save to json
        queue['message_id'] = new_messages

    update_db()

    await ctx.send('B1 up.')


# make counter embed
def make_counter():
    now = datetime.datetime.now()
    counter_embed = discord.Embed(color=0x6d2c2c)
    counter_embed.set_thumbnail(url='https://media.discordapp.net/attachments/286838882392080384/769995627484151818'
                                    '/1580219100588.gif')
    counter_embed.add_field(name=f"CB {now.strftime('%B %Y')}", value=f'\u200b', inline=False)
    counter_embed.add_field(name="Current Round", value='1', inline=True)
    counter_embed.add_field(name="Current Tier", value='1', inline=True)
    counter_embed.add_field(name="Current Boss", value='1', inline=False)
    return counter_embed


# make queue table embed  with round number as parameter
def make_queue_table(round_num):
    table_embed = discord.Embed(title=f'Round {round_num}',
                                color=0x06ade5)
    table_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/163948097330741248/770594243668475904'
                                  '/20201027_212605.jpg')
    for i in range(5):
        table_embed.add_field(name=f'B{i + 1}',
                              value='???',
                              inline=False)
    return table_embed


# check if queue is active
def is_active():
    if 'active' not in queue:
        return False

    return queue['active']


# convert emoji to integer
def get_boss_index(emoji):
    index = 0
    for reaction in reactions:
        if str(emoji) == reaction:
            return index
        index += 1


# proceed with the queue
def increment_current(round, boss):
    current_round = round
    current_boss = boss + 1

    if current_boss > 5:
        current_round += 1
        current_boss = 1

    current_tier = calculate_tier(current_round)

    return current_round, current_tier, current_boss

# calculates tier depending on the round given
def calculate_tier(round):
    if round >= 45:
        return 5
    elif round >= 35:
        return 4
    elif round >= 11:
        return 3
    elif round >= 4:
        return 2
    else:
        return 1

# update database
def update_db():
    collection = get_collection()

    collection.delete_one({'active': True})
    if queue:
        collection.insert_one(queue)

# load data from database
def load_from_db():
    collection = get_collection()
    global queue

    results = collection.find({'active': True})
    for result in results:
        if result:
            queue = result

# get collection from database
def get_collection():
    mongo_client = MongoClient(os.getenv('DATABASE_URL'))
    db = mongo_client[os.getenv('DATABASE_NAME')]
    return db[os.getenv('DATABASE_COLLECTION')]


# run the discord client
client.run(os.getenv('TOKEN'))
