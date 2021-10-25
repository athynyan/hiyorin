import discord

from modules.helpers.queue import v2 as v2_helper
from modules.reactions import queue
from modules.queue import v1, v2

from modules.helpers import roles as role_helper
from modules import roles
from utils.postgres import get_roles

from modules.helpers.checks import *
from discord.ext import commands


class Queue(commands.Cog):
    def __init__(self, client):
        self.client = client

    # DISCORD EVENTS
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = await self.client.fetch_user(payload.user_id)
        if user.bot:
            return

        guild = self.client.get_guild(payload.guild_id)

        await queue.add_reaction(payload, user, guild)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = await self.client.fetch_user(payload.user_id)
        if user.bot:
            return

        guild = self.client.get_guild(payload.guild_id)

        await queue.remove_reaction(payload, user, guild)

    # DISCORD COMMANDS
    # CREATE A QUEUE ENTRY FOR THE SERVER THAT CALLED THIS COMMAND
    @commands.command()
    @can_use_command(admin=True)
    @is_queue_active(False)
    async def start(self, ctx, queue_length=1, new_system=True):

        if new_system:
            await v2.start(ctx)
        else:
            await v1.start(ctx, queue_length)

        # DELETE COMMAND MESSAGE
        await ctx.message.delete()

    # ENDS THE QUEUE
    @commands.command()
    @can_use_command(admin=True)
    @is_queue_active(True)
    async def end(self, ctx):
        remove_document('server_id', ctx.message.guild.id, os.getenv('MONGO_DB_QUEUE'))
        await ctx.channel.purge(limit=10)

    # KILL COMMANDS
    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def kill(self, ctx, boss=0, damage=0, done=False):
        if boss > 0:
            await v2.kill(ctx, boss, damage, done)
        else:
            v1.kill()

    # KILL COMMANDS FOR QUEUE VERSION 2
    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k1(self, ctx, *args):
        damage, done = v2_helper.get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=1, damage=damage, done=done)

    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k2(self, ctx, *args):
        damage, done = v2_helper.get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=2, damage=damage, done=done)

    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k3(self, ctx, *args):
        damage, done = v2_helper.get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=3, damage=damage, done=done)

    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k4(self, ctx, *args):
        damage, done = v2_helper.get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=4, damage=damage, done=done)

    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k5(self, ctx, *args):
        damage, done = v2_helper.get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=5, damage=damage, done=done)

    @commands.command()
    async def rm(self, ctx, boss, member):
        pass

    @commands.command(name='addr')
    @commands.has_permissions(manage_messages=True)
    async def add_role(self, ctx, *args):
        role_id, admin = role_helper.get_args(args)

        print(f'{role_id}: {admin}')
        try:
            roles.add_role(role_id, ctx.message.guild.roles, admin)
        except (discord.ext.commands.errors.CommandInvokeError, IndexError, AttributeError, TypeError) as e:
            print(e)

    @commands.command(name='r')
    @can_use_command(admin=True)
    async def print_role(self, ctx):
        role_list = get_roles()
        print(role_list)

    @commands.command(name='rmr')
    @commands.has_permissions(manage_messages=True)
    async def remove_role(self, ctx, role_mention):
        role_id = int(role_mention[3:-1])
        try:
            roles.remove_role(role_id, ctx.message.guild.roles)
        except (discord.ext.commands.errors.CommandInvokeError, IndexError, AttributeError) as e:
            print(e)

    # PROCEED TO NEXT ROUND
    @commands.command()
    @can_use_command(admin=True)
    @is_queue_active(True)
    async def next(self, ctx, round=1):
        pass


def setup(client):
    client.add_cog(Queue(client))
