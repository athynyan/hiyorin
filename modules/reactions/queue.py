import os

from utils.mongo import get_document
from modules.queue.v2 import queue_field

reaction_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']


async def add_reaction(payload, user, guild):
    queue = get_document('server_id', guild.id, os.getenv('MONGO_DB_QUEUE'))
    if not queue:
        return

    if queue['new_system']:
        await add_v2(payload, queue, guild, user)
    else:
        await add_v1(payload, queue, guild, user)


async def remove_reaction(payload, user, guild):
    queue = get_document('server_id', guild.id, os.getenv('MONGO_DB_QUEUE'))
    if not queue:
        return

    if queue['new_system']:
        await remove_v2(payload, queue, guild, user)
    else:
        await remove_v1(payload, queue, guild, user)


async def add_v1(payload, queue, guild, user):
    boss_index = get_boss_index(payload.emoji)
    for message_id in queue['message_ids']:
        if message_id == payload.message_id:
            message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
            embed = message.embeds[0]
            name = embed.fields[boss_index].name.split(' ')

            if embed.fields[boss_index].value == '???':
                embed.set_field_at(boss_index, name=f'{name[0]} {name[1]}', value=user.mention, inline=False)
            else:
                # store existing values from embed into a temporary list
                mentions = embed.fields[boss_index].value.split(',')
                # check for duplicate users
                if user.mention in mentions:
                    return

                # append user to the embed
                mentions.append(user.mention)
                embed.set_field_at(boss_index, name=f'{name[0]} {name[1]}', value=','.join(mentions), inline=False)

                # apply changes to the message
            await message.edit(embed=embed)


async def remove_v1(payload, queue, guild, user):
    boss_index = get_boss_index(payload.emoji)
    for message_id in queue['message_ids']:
        if message_id == payload.message_id:
            message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
            embed = message.embeds[0]
            name = embed.fields[boss_index].name.split(' ')

            if embed.fields[boss_index].value == '???':
                return

            mentions = embed.fields[boss_index].value.split(',')

            if user.mention not in mentions:
                return

            mentions.remove(user.mention)
            if mentions:  # check if list is not empty
                embed.set_field_at(boss_index, name=f'{name[0]} {name[1]}', value=','.join(mentions), inline=False)
            else:
                embed.set_field_at(boss_index, name=f'{name[0]} {name[1]}', value='???', inline=False)

            # apply changes to the message
            await message.edit(embed=embed)


async def add_v2(payload, queue, guild, user):
    if payload.message_id in queue['message_ids']:
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        embed = message.embeds[0]

        user_list = embed.fields[queue_field['user_list']].value.split('\n')

        if '???' in user_list:
            user_list.clear()

        if user.mention not in user_list:
            user_list.append(user.mention)

        embed.set_field_at(queue_field['user_list'], name='Queue', value='\n'.join(user_list))
        await message.edit(embed=embed)


async def remove_v2(payload, queue, guild, user):
    if payload.message_id in queue['message_ids']:
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        embed = message.embeds[0]

        user_list = embed.fields[queue_field['user_list']].value.split('\n')

        if user.mention in user_list:
            user_list.remove(user.mention)

        if not user_list:
            user_list.append('???')

        embed.set_field_at(queue_field['user_list'], name='Queue', value='\n'.join(user_list))
        await message.edit(embed=embed)


def get_boss_index(emoji):
    index = 0
    for reaction in reaction_list:
        if str(emoji) == reaction:
            return index
        index += 1
