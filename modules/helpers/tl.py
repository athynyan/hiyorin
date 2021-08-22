from utils.postgres import get_character_dicts
import re


def format_tl_input(input_string):
    formatted_input = []
    general_info = []
    party_setup = []
    timeline = []
    character_dict, alt_dict = get_character_dicts()

    # split input_string list into sublists and save to formatted_input list
    for sublist in [subl.split(' ') for subl in ' '.join(input_string).split('----')]:
        formatted_input.append(list(filter(None, sublist)))

    # mapping character names to english
    for character in character_dict:
        for i in range(len(formatted_input[1])):
            words = formatted_input[1][i].split('（')
            if character[1] == words[0]:
                formatted_input[1][i] = formatted_input[1][i].replace(character[1], character[2])
        for i in range(len(formatted_input[2])):
            words = formatted_input[2][i].split('（')
            if character[1] == words[0]:
                formatted_input[2][i] = formatted_input[2][i].replace(character[1], character[2])

    # mapping alt versions to english
    for alt in alt_dict:
        for i in range(len(formatted_input[1])):
            if alt[1] in formatted_input[1][i]:
                formatted_input[1][i] = formatted_input[1][i].replace(alt[1], alt[2])
        for i in range(len(formatted_input[2])):
            if alt[1] in formatted_input[2][i]:
                formatted_input[2][i] = formatted_input[2][i].replace(alt[1], alt[2])

    # General Info
    tier = [s for s in formatted_input[0] if "段階目" in s].pop().removesuffix('段階目')
    damage = [s for s in formatted_input[0] if "ダメージ" in s].pop().removesuffix('ダメージ')
    general_info.append(f'Boss: {formatted_input[0][2]}')
    general_info.append(f'Tier: {tier}')
    general_info.append(f'Damage: {damage}')

    # Party Setup
    formatted_input[1].pop(0)
    chunks = [formatted_input[1][x:x + 4] for x in range(0, len(formatted_input[1]), 4)]
    for chunk in chunks:
        chunk.reverse()
        party_setup.append(' '.join(chunk))

    # Timeline
    for i in range(3):
        formatted_input[2].pop(0)
    time_regex = re.compile('0((1:([0-2][0-9]|30))|(0:[0-5][0-9]))')
    temporary_list = []
    for element in formatted_input[2]:
        match = time_regex.search(element)
        if match:
            timeline.append(' '.join(temporary_list))
            temporary_list.clear()
        if element == formatted_input[0][2]:
            temporary_list.append('**BOSS UB**')
        else:
            temporary_list.append(element)

    return '\n '.join(general_info), '\n '.join(party_setup), '\n '.join(timeline), ''