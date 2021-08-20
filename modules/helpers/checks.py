import discord
from discord.ext import commands
from utils.mongo import *


def is_queue_active(boolean):
    async def predicate(ctx):
        active = False
        if get_document('server_id', ctx.message.guild.id, os.getenv('MONGO_DB_QUEUE')):
            active = True
        return not (active ^ boolean)
    return commands.check(predicate)
