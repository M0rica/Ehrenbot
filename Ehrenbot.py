import asyncio
import random
import os
import sys
import time
from datetime import datetime
from shutil import rmtree, copytree

import discord
from discord.ext import commands

sys.path.append(f'{os.getcwd()}/classes')
sys.path.append(f'{os.getcwd()}/utils')

from Server import Server
from utils import log, has_permission

intents = discord.Intents.all()
client = commands.Bot(command_prefix='ehre ', help_command=None, intents=intents)

servers = {}

activities = ['ehre help', 'You suck', 'Reißt die Weltherrschaft an sich', 'Überwacht euch', 'Ich seh alles!', 'Ich hasse dich nicht']


@client.event
async def on_ready():
    log('Bot ready', )

    for guild in client.guilds:
        servers[guild.id] = Server(client, guild)

    await asyncio.sleep(10)

    while True:

        await asyncio.sleep(10)

        for server in servers:
            await servers[server].update()

        await asyncio.sleep(10)

        for server in servers:
            servers[server].save()

        await asyncio.sleep(10)

        await client.change_presence(activity=discord.Game(random.choice(activities)))

        await asyncio.sleep(10)


@client.event
async def on_guild_join(guild):
    log(f'Joined new server {guild.name}')
    servers[guild.id] = Server(client, guild)


@client.event
async def on_member_join(member):
    servers[member.guild.id].add_member(member)


@client.event
async def on_message(ctx):

    if not ctx.author.bot:

        await servers[ctx.guild.id].process_msg(ctx)

        if ctx.channel.category.name == 'ehrenbot':

            if ctx.channel.name == 'ehrenwerte-tabelle':

                await ctx.delete()
            else:

                msg = await client.get_context(ctx)
                if msg.valid:
                    await client.process_commands(ctx)


@client.command(aliases=['shut'])
async def shutdown(ctx):

    if has_permission(ctx.author, ctx.guild, 3):

        log('Stopping bot...')

        for server in servers:
            servers[server].save()

        answers = ["Goodbye :wave:", "Thänk ju vor träwelling with Deutsche Bahn :bullettrain_front:",
                   "Bye have a great time", "Und tschüss", "Ich mach dann mal nen Abgang",
                   "Bot ist müde und geht schlafen :sleeping:", "Bruder muss los :runner:"]
        answer = random.choice(answers)
        await ctx.send(answer)
        await client.change_presence(status=discord.Status.idle, activity=discord.Game('Gute Nacht'))

        await client.close()
        time.sleep(3)

        loop = asyncio.get_event_loop()
        loop.stop()
        loop.run_until_complete(loop.shutdown_asyncgens())

        #sys.exit()

    else:

        await ctx.send('Du hast nicht die Berechtigungen für diesen Befehl!', delete_after=10)

@client.command(aliases=['Stats', 'statistics', 'Statistics'])
async def stats(ctx):

    guild = servers[ctx.guild.id]


    emb = discord.Embed(title=guild.name, description=guild.get_stats(), colour=random.randint(0, 16777215))
    await ctx.send(embed=emb)


@client.command()
async def donate(ctx, donate_to: discord.Member):

    await servers[ctx.guild.id].donate(ctx, donate_to.id)

@client.command(aliases=["Verlauf", "konto", "Konto"])
async def verlauf(ctx, mode="public"):

    await servers[ctx.guild.id].member_ehre_history(ctx, mode)

@client.command(aliases=['vote', 'Votum', 'Vote'])
async def votum(ctx, to_member: discord.Member, ammount, *, reason):

    if not to_member.bot:

        await servers[ctx.guild.id].create_vote(ctx, to_member.id, ammount, reason)
    else:
        emb = discord.Embed(title='Ehrenvotum :ballot_box:',description=f'Du kannst keine Abstimmung für einen Bot erstellen!',colour=random.randint(0, 16777215))
        await ctx.send(embed=emb)

@client.command()
async def donations(ctx, action=''):

    desc = ''
    server = servers[ctx.guild.id]

    if action:

        if action == 'reset':

            if has_permission(ctx.author, ctx.guild, 2):

                desc = server.reset_donations()

            else:

                desc = ':x: Du hast keine Rechte und darfst deswegen diese Aktion nicht ausführen! \nPech gehabt... :cry:'

    else:

        desc = server.get_donations()

    emb = discord.Embed(title='Donations', description=desc, colour=random.randint(0, 16777215))
    await ctx.send(embed=emb)

@client.command()
async def help(ctx, mode=''):

    await ctx.send(embed=servers[ctx.guild.id].help(mode, ctx.author.id))

@client.command()
async def settings(ctx, setting='', mode=''):

    if has_permission(ctx.author, ctx.guild, 2):
        desc = servers[ctx.guild.id]._settings(setting, mode)
    else:
        desc = 'Zugriff verweigert'

    emb = discord.Embed(title='Settings :memo:', description=desc, colour=random.randint(0, 16777215))
    await ctx.send(embed=emb)


folders = ["guild_data", "guild_data/_backups", "guild_data/_default", "guild_data/_default/logs"]
for folder in folders:
    if os.path.isdir(folder):
        pass
    else:
        os.mkdir(folder)
log('Starting bot')

client.run('TOKEN')

log('Bot stopped', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
