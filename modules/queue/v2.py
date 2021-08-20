from modules.helpers.queue.v2 import *
from utils.mongo import *

queue_field = {
    'current_round': 0,
    'current_tier': 1,
    'hp': 2,
    'user_list': 3
}


async def start(context, queue_length):
    # GENERATES QUEUE EMBEDS AND SAVES THE MESSAGE IDS INTO A LIST
    embed_list = make_queue_embed_list()
    messages = await send_queue(context, embed_list)

    # MAKE A NEW DB ENTRY
    queue = {'server_id': context.message.guild.id,
             'channel_id': context.message.channel.id,
             'message_ids': messages,
             'queue_length': queue_length,
             'new_system': True}
    add_document(queue, os.getenv('MONGO_DB_QUEUE'))


async def kill(context, boss, damage, done):
    queue = get_document('server_id', context.message.guild.id, os.getenv('MONGO_DB_QUEUE'))
    message = await context.message.guild.get_channel(queue['channel_id']).fetch_message(queue['message_ids'][boss - 1])

    embed = message.embeds[0]

    hp = int(embed.fields[queue_field['hp']].value) - damage
    tier = int(embed.fields[queue_field['current_tier']].value)

    if hp <= 0 or damage <= 0:
        new_round = int(embed.fields[queue_field['current_round']].value) + 1
        next_tier = get_tier(new_round)
        hp = hp_list[boss][get_tier(new_round) - 1]

        embed.set_field_at(0, name='Current Round', value=str(new_round))
        if tier < next_tier:
            embed.set_field_at(queue_field['current_tier'], name='Current Tier', value=str(next_tier))

        await message.clear_reactions()
        await message.add_reaction('✅')

    embed.set_field_at(queue_field['hp'], name='HP', value=str(hp), inline=False)

    if done:
        user_list = embed.fields[queue_field['user_list']].value.split('\n')
        await context.message.channel.send(user_list.pop(0))
        if not user_list:
            user_list.append('???')

        embed.set_field_at(queue_field['user_list'], name='Queue', value='\n'.join(user_list), inline=False)

    await message.edit(embed=embed)


