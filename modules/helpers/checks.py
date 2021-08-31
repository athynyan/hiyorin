from discord.ext import commands
from utils.mongo import *
from utils.postgres import get_roles


def is_queue_active(boolean):
    async def predicate(ctx):
        active = False
        if get_document('server_id', ctx.message.guild.id, os.getenv('MONGO_DB_QUEUE')):
            active = True
        return not (active ^ boolean)
    return commands.check(predicate)


def can_use_command(admin=False):
    async def predicate(ctx):
        return [True for author_role in ctx.message.author.roles for role in get_roles() if author_role.id in role].pop()
    return commands.check(predicate)
