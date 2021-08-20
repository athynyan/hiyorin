import datetime
import discord
from utils.mongo import *
from modules.reactions.queue import reaction_list


async def start(context, queue_length):
    # GENERATES A COUNTER EMBED FOR TRACKING ROUNDS
    counter_embed = make_counter_embed()
    counter = await context.message.channel.send(embed=counter_embed)

    # GENERATES QUEUE EMBEDS AND SAVES THE MESSAGE IDS INTO A LIST
    queue_embeds = make_queue_embed_list(queue_length)
    messages = await send_queue(context, queue_embeds)

    # MAKE A NEW DB ENTRY
    queue = {'server_id': context.message.guild.id,
             'channel_id': context.message.channel.id,
             'counter_id': counter.id,
             'message_ids': messages,
             'queue_length': queue_length,
             'new_system': False}
    add_document(queue, os.getenv('MONGO_DB_QUEUE'))


async def go_to_round(client, context, round):
    queue = get_document('server_id', context.message.guild.id, os.getenv('MONGO_DB_QUEUE'))
    channel = client.get_channel(queue['channel_id'])

    for message_id in queue['message_ids']:
        message = await channel.fetch_message(message_id)

        embed = message.embeds[0].set_field_at(1, name='Round', value=5)
        await message.edit(embed=embed)


async def go_next_round(context):
    queue = get_document('server_id', context.message.guild.id, os.getenv('MONGO_DB_QUEUE'))
    pass


# SEND QUEUE AS EMBED MESSAGES AND PUT REACTIONS
async def send_queue(context, queue_embeds):
    messages = []
    for embed in queue_embeds:
        message = await context.message.channel.send(embed=embed)
        messages.append(message.id)
        for reaction in reaction_list:
            await message.add_reaction(reaction)
    return messages


# MAKES AN EMBED TO TRACK ROUNDS
def make_counter_embed():
    now = datetime.datetime.now()
    counter_embed = discord.Embed(color=0x6d2c2c)
    counter_embed.set_thumbnail(url='https://media.discordapp.net/attachments/286838882392080384/769995627484151818'
                                    '/1580219100588.gif')
    counter_embed.add_field(name=f"CB {now.strftime('%B %Y')}", value=f'\u200b', inline=False)
    counter_embed.add_field(name="Current Round", value='1', inline=True)
    counter_embed.add_field(name="Current Tier", value='1', inline=True)
    return counter_embed


# MAKES LIST WITH EMBEDS FOR THE QUEUE
def make_queue_embed_list(number_of_embeds):
    embed_list = []
    for i in range(number_of_embeds):
        embed_list.append(make_queue_embed(i + 1))
    return embed_list


# MAKES A SINGLE EMBED OBJECT
def make_queue_embed(round):
    queue_embed = discord.Embed(title=f'Round {round}',
                                color=0x06ade5)
    queue_embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/163948097330741248/770594243668475904/20201027_212605.jpg')

    for i in range(5):
        queue_embed.add_field(name=f'B{i + 1}',
                              value='???',
                              inline=False)
    return queue_embed


def kill():
    return None
