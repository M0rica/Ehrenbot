import asyncio
import random
import os
import sys
import time
from datetime import datetime
import argparse

import discord
from discord.ext import commands

sys.path.append(f'{os.getcwd()}/classes')
sys.path.append(f'{os.getcwd()}/utils')

from Server import Server
from utils import log, has_permission, admin

intents = discord.Intents.all()
client = commands.Bot(command_prefix='ehre ', help_command=None, intents=intents)

reboot = False
devmode = False

servers = {}

activities = ['ehre help', 'You suck', 'Reißt die Weltherrschaft an sich', 'Überwacht euch', 'Ich seh alles!', 'Ich hasse dich nicht']

async def bot_shutdown(ctx):

    log('Stopping bot...')

    for server in servers:
        servers[server].save()

    answers = ["Goodbye :wave:", "Thänk ju vor träwelling with Deutsche Bahn :bullettrain_front:",
               "Bye have a great time", "Und tschüss", "Ich mach dann mal nen Abgang",
               "Bot ist müde und geht schlafen :sleeping:", "Bruder muss los :runner:"]
    answer = random.choice(answers)
    await ctx.channel.send(answer)
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('Gute Nacht'))

    await client.close()
    time.sleep(3)

    loop = asyncio.get_event_loop()
    loop.stop()
    loop.run_until_complete(loop.shutdown_asyncgens())


@client.event
async def on_ready():
    log('Bot ready', )

    for guild in client.guilds:
        servers[guild.id] = Server(client, guild)

    await asyncio.sleep(10)

    while True:

        await asyncio.sleep(10)

        log('Updating Servers')
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
                    if devmode and str(ctx.author) != admin:
                        await ctx.channel.send(embed=discord.Embed(title=':warning: Devmode aktiv :warning:',
                                                                 description='Der Bot befindet sich grade im Testmodus, Bugfixes oder neue Features werden getestet weshalb vorrübergehend keine Kommands zur Verfügung stehen!',
                                                                    colour=random.randint(0, 16777215)))
                    else:
                        await client.process_commands(ctx)

                elif has_permission(ctx.author, ctx.guild, 3) and ctx.content.startswith('//') or ctx.content.startswith('dev'):

                    aliases = {
                        'reboot': 'reload',
                        'shut': 'shutdown',
                        'devmode': 'testmode'
                    }


                    func = ctx.content.replace('//', '')
                    if func in aliases:
                        func = aliases[func]
                    func += '(ctx)'
                    await eval(func)


async def shutdown(ctx):

    if has_permission(ctx.author, ctx.guild, 3):

        await bot_shutdown(ctx)

    else:

        await ctx.send('Du hast nicht die Berechtigungen für diesen Befehl!', delete_after=10)


async def reload(ctx):

    if has_permission(ctx.author, ctx.guild, 3):

        global reboot
        await ctx.channel.send('Bot wird neu gestartet...')
        reboot = True
        await bot_shutdown(ctx)

    else:

        await ctx.send('Du hast nicht die Berechtigungen für diesen Befehl!', delete_after=10)

async def testmode(ctx):

    global devmode
    if devmode:
        devmode = False
        desc = 'Devmode deaktiviert!'
    else:
        devmode = True
        desc = 'Devmode aktiviert!'

    await ctx.channel.send(desc)

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

@client.command(aliases=['account'])
async def profile(ctx, member: discord.Member=None):

    desc = ''
    profile_pic = None
    member = ctx.author if not member else member

    if member == ctx.author or has_permission(ctx.author, ctx.guild, 2):

        if not member.bot:
            desc = servers[ctx.guild.id].get_profile(member.id)
            profile_pic = member.avatar_url

        else:
            desc = 'Bots haben keine Accounts!'

    else:
        desc = 'Zugriff verweigert'

    emb = discord.Embed(title='Member profile', description=desc, colour=random.randint(0, 16777215))
    emb.set_thumbnail(url=profile_pic)
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

parser = argparse.ArgumentParser(description='Basic parser for Ehrenbot')

parser.add_argument('--devmode', default=False, action='store_true', help='start bot in devmode')

args = parser.parse_args()
devmode = args.devmode

folders = ["guild_data", "guild_data/_backups", "guild_data/_default", "guild_data/_default/logs"]
for folder in folders:
    if os.path.isdir(folder):
        pass
    else:
        os.mkdir(folder)
log('Starting bot')

client.run('TOKEN')

log('Bot stopped', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
if reboot:
    log('Reboot', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    time.sleep(3)
    os.execv(sys.executable, ['python'] + sys.argv + (['--devmode'] if devmode else []))

