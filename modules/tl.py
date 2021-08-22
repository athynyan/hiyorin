import discord
from modules.helpers.tl import format_tl_input


def make_tl_embed(input_string):
    general, party, timeline, additional_info = format_tl_input(input_string)

    embed = discord.Embed(color=0x657ed4)
    embed.add_field(name='General Info', value=general, inline=False)
    embed.add_field(name='Party Setup', value=party, inline=False)
    embed.add_field(name='Timeline', value=timeline, inline=False)
    if additional_info:
        embed.add_field(name='Additional Info', value=additional_info, inline=False)
    return embed
