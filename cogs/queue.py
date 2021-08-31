import discord

from modules.helpers.queue.v2 import get_args
from modules.reactions import queue
from modules.queue import v1, v2
from modules.helpers.checks import *
from discord.ext import commands
from utils.postgres import add_role, remove_role, get_roles


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
    @commands.has_role('Labyrinth Crepe Shop')
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
    @commands.has_role('Labyrinth Crepe Shop')
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
        damage, done = get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=1, damage=damage, done=done)

    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k2(self, ctx, *args):
        damage, done = get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=2, damage=damage, done=done)

    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k3(self, ctx, *args):
        damage, done = get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=3, damage=damage, done=done)

    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k4(self, ctx, *args):
        damage, done = get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=4, damage=damage, done=done)

    @commands.command()
    @can_use_command()
    @commands.cooldown(1, 15)
    @is_queue_active(True)
    async def k5(self, ctx, *args):
        damage, done = get_args(args)
        await ctx.invoke(self.client.get_command('kill'), boss=5, damage=damage, done=done)

    @commands.command()
    async def rm(self, ctx, boss, member):
        pass

    @commands.command(name='addr')
    async def add_role(self, ctx, role_mention):
        try:
            role = [role for role in ctx.message.guild.roles if role.id == int(role_mention[3:-1])].pop()
            add_role(role.id, role.name)
        except (discord.ext.commands.errors.CommandInvokeError, IndexError, AttributeError) as e:
            print(e)

    @commands.command(name='r')
    @can_use_command()
    async def print_role(self, ctx):
        guild_roles = ctx.message.guild.roles
        roles = get_roles()
        print(roles)
        print(guild_roles[-1].id)

    @commands.command(name='rmr')
    async def remove_role(self, ctx, role_mention):
        try:
            role = [role for role in ctx.message.guild.roles if role.id == int(role_mention[3:-1])].pop()
            remove_role(role.id)
        except (discord.ext.commands.errors.CommandInvokeError, IndexError, AttributeError) as e:
            print(e)

    # PROCEED TO NEXT ROUND
    @commands.command()
    @commands.has_role('Labyrinth Crepe Shop')
    @is_queue_active(True)
    async def next(self, ctx, round=1):
        pass


def setup(client):
    client.add_cog(Queue(client))
