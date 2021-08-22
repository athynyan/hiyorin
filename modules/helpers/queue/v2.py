import discord

color_list = [
    0x845EC2,
    0xD65DB1,
    0xFF6F91,
    0xFF9671,
    0xFFC75F
]
hp_list = {
    1: [6000000, 6000000, 12000000, 19000000, 85000000],
    2: [8000000, 8000000, 14000000, 20000000, 90000000],
    3: [10000000, 10000000, 17000000, 23000000, 95000000],
    4: [12000000, 12000000, 19000000, 25000000, 100000000],
    5: [15000000, 15000000, 22000000, 27000000, 110000000],
}


def make_queue_embed_list():
    embed_list = []
    for i in range(5):
        embed = discord.Embed(
            title=f"Boss {i + 1}",
            color=color_list[i]
        )
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/163948097330741248/770594243668475904'
                '/20201027_212605.jpg'
        )
        embed.add_field(
            name='Current Round',
            value='1',
        )
        embed.add_field(
            name='Current Tier',
            value='1'
        )
        embed.add_field(
            name='HP',
            value=str(hp_list[i + 1][0]),
            inline=False
        )
        embed.add_field(
            name='Queue',
            value='???',
            inline=False
        )
        embed_list.append(embed)
    return embed_list


async def send_queue(context, embed_list):
    messages = []

    for embed in embed_list:
        message = await context.message.channel.send(embed=embed)
        await message.add_reaction('✅')
        messages.append(message.id)

    return messages


def get_tier(round):
    return 1 if round < 4 else 2 if round < 11 else 3 if round < 31 else 4 if round < 41 else 5


def get_args(args):
    damage = [int(arg) for arg in args if arg.isnumeric()]
    done = [True for arg in args if arg == 'd']

    if not damage:
        damage = [0]
    if not done:
        done = [False]

    return damage.pop(0), done.pop(0)