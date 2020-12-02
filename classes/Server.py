import os
import json
import asyncio
import datetime
import random

from Member import Member
from Vote import Vote
from Exceptions import TransactionError
from utils import log, has_permission

import discord
from discord.utils import get


class Server:

    def __init__(self, client, guild: discord.Guild):

        self.client = client

        self.name = guild.name
        self.guild_obj = guild
        self.server_id = guild.id
        self.save_dir = f'guild_data/{self.server_id}'
        self.updates = 0
        members = guild.members

        self.settings = {
            "role": self.guild_obj.default_role,

            "anti_spam": "on",
            "spam_block_time": 10,

            "vote_time": 2,

            "lottery_mode": "off",
        }

        self.blocked_users = {}
        self.warned_users = []
        self.lottery = {}
        self.votes = {}

        self.description_text = 'Das war ein großer Fehler...\nKurz zu mir: **Wer bin ich?**\nNun, ich bin Ehrenbot (23) und starker :beer: Alkoholiker.\n\n' \
                                'Nee Spaß, ich bin ab sofort dafür zuständig, dass sich alle Mitglieder auf diesem Server ehrenhaft verhalten. Dazu wird jeder von euch mit der virtuellen ' \
                                'Währung :dollar: Ehre bewertet. Diese kann :chart_with_downwards_trend: sinken, solltet ihr zum Beispiel die Textchannels zuspamen oder sie kann durch Votes anderer Mitglieder abgezogen werden. ' \
                                'Es gibt aber natürlich auch die Möglichkeit sich Ehre zu verdiehnen :chart_with_upwards_trend:. Dies kann ebenfalls durch Votes passieren, da diese nicht nur Ehre abziehen, sondern auch geben können. ' \
                                'Zusätzlich hat jeder einmal Täglich die Möglichkeit, 10 Ehre an einen Member seiner Wahl zu geben :money_with_wings:.\n\nUm über alle Funktionen und deren gebrauch zu erfahren, einfach `ehre help` eingeben.\n\n' \
                                'Sollte sich jemand nicht an meine Regeln oder die Regeln des Servers halten, ist es mir ein Vergnügen denjenigen darauf aufmerksam zu machen :smiling_imp:.'


        if self.has_saved_data():
            self.log('Loading saved server data...')
            self.load()

        else:
            log('Setting up new server...')
            asyncio.run_coroutine_threadsafe(self.setup(), asyncio.get_event_loop())

        self.members = {}
        for member in members:

            if not member.bot:
                member_obj = Member(member.id, member.display_name, self.save_dir)

                self.members[member.id] = member_obj

        vote_threshold = int(round(len(self.members) / 12.5))
        self.settings["vote_threshold"] = vote_threshold if vote_threshold >= 3 else 3


    #======SYSTEM INTERNAL FUNCTIONS======#

    def has_saved_data(self):

        return os.path.isdir(self.save_dir)

    #=====Log special events to server specific file and systemwide file=====#
    def log(self, info):

        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log(info, timestamp, self.name)

        info = f'[{timestamp}] {info}\n'
        with open(f'{self.save_dir}/logs/{datetime.datetime.now().strftime("%d_%m_%Y")}.log', 'a') as f:
            f.write(info)

    #=====Save data to disk=====#
    def save(self):

        self.log('Saving server data...')
        with open(f'{self.save_dir}/data.json', 'w') as save:
            data = {}
            data["settings"] = {
                "role": self.settings["role"].id,

                "anti_spam": self.settings["anti_spam"],
                "spam_block_time": self.settings["spam_block_time"],

                "vote_time": self.settings["vote_time"],
                "vote_threshold": 2,

                "lottery_mode": self.settings["lottery_mode"]
            }
            data["blocked_users"] = self.blocked_users
            data["table_channel"] = self.table_channel.id
            data["default_channel"] = self.default_channel.id
            data["table_id"] = self.table_id
            votes = [{v: self.votes[v].to_dict()} for v in self.votes]
            data["votes"] = votes
            json.dump(data, save, indent=4)

        for member in self.members:
            self.members[member].save()

    #=====Load data from disk=====#
    def load(self):

        try:
            with open(f'{self.save_dir}/data.json', 'r') as save:
                data = json.load(save)

            self.settings = data["settings"]
            self.settings["role"] = get(self.guild_obj.roles, id=self.settings["role"])
            self.blocked_users = data["blocked_users"]
            self.table_channel = data["table_channel"]
            self.table_channel = self.guild_obj.get_channel(self.table_channel)
            self.default_channel = data["default_channel"]
            self.default_channel = self.guild_obj.get_channel(self.default_channel)
            self.table_id = data["table_id"]
            self.votes = {v: Vote.from_dict(data["votes"][v]) for v in data["votes"]}

            if self.table_channel == None or self.default_channel == None:

                asyncio.run_coroutine_threadsafe(self.create_discord_channels(), asyncio.get_event_loop())

            new_blocked_list = {}
            self.blocked_users = new_blocked_list

            self.log('Successfully loaded saved data!')
        except Exception as e:

            print(e)
            asyncio.run_coroutine_threadsafe(self.repair(), asyncio.get_event_loop())


    #=====Set new server up, either on join or on reboot=====#
    async def setup(self):

        log('Creating folders...', server=self.name)

        folders = ['accounts', 'logs']

        os.mkdir(self.save_dir)

        for folder in folders:
            os.mkdir(f'{self.save_dir}/{folder}')

        open(f'{self.save_dir}/{self.name}', 'a').close() # Server folders are named after their discord server ids, file with real server name for clarification

        self.log('Creating discord channels...')

        await self.create_discord_channels()

        self.log('Sending default messages...')

        emb = discord.Embed(title='Vielen Dank, dass ihr mich auf euren Server gelassen habt!',
                            description=self.description_text, colour=random.randint(0, 16777215))

        await self.default_channel.send(embed=emb)

        self.log('Successfully send messages!')

        self.log('Setup completed!')
        self.save()

    #=====Try to repair server if data or channels are missing=====#
    async def repair(self):

        self.log('An error occurred while loading saved data, trying to repair server data...')
        self.set_default_settings()
        await self.create_discord_channels()

    #=====Create standart discord channels on a server, either called on setup or repair=====#
    async def create_discord_channels(self):

        category_exists = False
        default_channel_exists = False
        table_channel_exists = False

        for cat in self.guild_obj.categories:

            if cat.name == 'ehrenbot':

                category_exists = True
                category = cat

                for channel in category.text_channels:

                    if channel.name == 'ehrenchannel':

                        default_channel_exists = True
                        self.default_channel = channel

                    elif channel.name == 'ehrenwerte-tabelle':

                        table_channel_exists = True
                        self.table_channel = channel
                        table_msg = await self.table_channel.history(oldest_first=True).flatten()
                        self.table_id = table_msg[0].id

        if not category_exists:

            category = await self.guild_obj.create_category('ehrenbot')

        if not default_channel_exists:

            self.default_channel = await self.guild_obj.create_text_channel('ehrenchannel', category=category, topic='Dieser channel ist ausschließlich für die Interaktion mit Ehrenbot dar.')

        if not table_channel_exists:

            self.table_channel = await self.guild_obj.create_text_channel('ehrenwerte-tabelle', category=category)

            emb = discord.Embed(title='Ehrenwerte Tabelle', colour=6614463)
            for member in self.members:
                account_field = f'```\n{self.members[member].balance} Ehre```'
                emb.add_field(name=f'**{self.members[member].name}**', value=account_field)

            msg = await self.table_channel.send(embed=emb)

            self.table_id = msg.id

    #=====Set default server settings if data is missing or corrupt=====#
    def set_default_settings(self):

        self.settings = {
            "role": self.guild_obj.default_role,

            "anti_spam": "on",
            "spam_block_time": 10,

            "vote_time": 15,
            "vote_threshold": 2,

            "lottery_mode": "off",
        }

    #=====Add new member to internal member list=====#
    def add_member(self, member):

        self.members[member.id] = Member(member.id, member.display_name, self.save_dir)

    #======NONE-INTERNAL FUNCTIONS======#

    def process_msg(self, ctx):

        member = self.members[ctx.author.id]
        msg = ctx.content
        msg_len = int(len(msg) / 100)
        msg_len = 1 if msg_len == 0 else msg_len
        member.antispam_score += msg_len

    #=====Update server events, such as votes=====#
    async def update(self):

        self.log('Updating...')

        self.updates += 1
        now = datetime.datetime.now()

        self.log('Refreshing Ehre table...')

        old_msg: discord.Message
        old_msg = await self.table_channel.fetch_message(self.table_id)

        emb = discord.Embed(title='Ehrenwerte Tabelle', colour=6614463)

        for member in self.members:


            account_field = f'```\n{self.members[member].balance} Ehre```'
            emb.add_field(name=f'**{self.members[member].name}**', value=account_field)

        await old_msg.edit(embed=emb)


        if self.updates % 5 == 0:

            vote_threshold = int(round(len(self.members) / 12.5))
            self.settings["vote_threshold"] = vote_threshold if vote_threshold > 3 else 3

            self.log('Updating player names...')
            for member in self.guild_obj.members:

                if not member.bot:
                    self.members[member.id].name = member.display_name

        # check for votes to be evaluated
        self.log('Evaluating votes...')
        for member in list(self.votes.keys()):

            vote = self.votes[member]

            votum_time = int(now.strftime("%H%M")) - int(vote.created_at)

            if votum_time >= vote.time:
                await self.eval_vote(member)

        self.log('Running antispam...')
        await self.perform_antispam()

    async def perform_antispam(self):

        for member in self.members.values():

            if member.antispam_score >= 12:

                if member.warned:
                    await self.suspend_member(member)

                else:
                    await self.warn_member(member)

            member.antispam_score = 0

    async def warn_member(self, member):

        member.warned = True
        self.transaction(member, -25, 'Vorwarnung für Spaming')
        member = self.guild_obj.get_member(member.member_id)

        await member.send('Weißt du, Spaming ist echt assozial, also entspann dich mal :island: Du willst doch keine Beurlaubung oder :face_with_raised_eyebrow:')
        self.log(f'Warned {member.display_name} for spaming')

    async def suspend_member(self, member):

        blocked_user_entry = {
            "blocked_at": int(datetime.datetime.now().strftime("%Y%m%d%H%M")),
            "block_time": self.settings["spam_block_time"]
        }
        self.blocked_users[member.member_id] = blocked_user_entry

        member.warned = False
        member.bans += 1
        self.transaction(member, -111, 'Spaming du Ehrenloser (+ 5 Peitschenhiebe)')
        self.log(f'Suspended {member.name} for {self.settings["spam_block_time"]}min for Spaming')

        member = self.guild_obj.get_member(member.member_id)
        await member.remove_roles(self.settings["role"])
        await member.send(f':partying_face: Herzlichen Glückwunsch! Du, ja, genau **du** hast dir eine {blocked_user_entry["block_time"]} Minuten Auszeit auf dem Server **{self.name}** verdient! Genieße sie!')
        await asyncio.sleep(3)
        await member.send('By the way, Spaming wird bei uns mit der Peitsche bestraft, trau dich nur wieder on zu kommen :smiling_imp:')

    #=====Reset daily donations for this server=====#
    def reset_donations(self):

        for member in self.members:

            member = self.members[member]
            member.donated = False

        return ':white_check_mark: Tägliche Spenden sind nun wieder verfügbar!'

    #=====Get who donated today and who didn't=====#
    def get_donations(self):

        donated = 0
        not_donated = 0

        for member in self.members:

            member = self.members[member]
            if member.donated:
                donated += 1
            else:
                not_donated += 1

        return f':white_check_mark: Members die donated haben: **{donated}**\n:x: Members die nicht donated haben: **{not_donated}**'


    #=====Evaluate a vote after set amount of time=====#
    async def eval_vote(self, member):

        vote = self.votes[member]
        member = self.members[int(member)]
        to_member = self.members[vote.to_member]

        channel = self.client.get_channel(vote.message_channel)
        emb, all_score, score = vote.eval(self, channel, self.settings["vote_threshold"], member, to_member, self.members)
        self.log(f'Evaluation of vote of {member.name}: Participants: {all_score}, Score: {score}')

        del self.votes[str(member.member_id)]
        member.has_vote = False

        await channel.send(embed=emb)


    def transaction(self, member, amount: int, note: str):

        try:
            member.transaction(amount, note)

        except TransactionError:
            pass


    #======DISCORD COMMANDS======#

    def _settings(self, setting, change):

        setting = setting.lower()
        desc = ''

        if not setting:

            desc += '**Aktuelle Settings**'
            desc += f'\n\nRolle für alle Textchannels: **{self.settings["role"]}**'

            desc += f'\nAnti-spam: **{self.settings["anti_spam"]}**'
            desc += f'\nBlockierung bei starkem Verstoß gegen Regeln: **{self.settings["spam_block_time"]} min**'

            desc += f'\nZeit für Abstimmungen: **{self.settings["vote_time"]} min**'
            desc += f'\nMindesbeteiligung für Abstimmungen: **{self.settings["vote_threshold"]} Personen**'

            desc += '\n\n Um mehr über einzelne Einstellungen zu erfahren oder um sie zu verändern, gib einfach `ehre settings <setting>` ein.'

        elif setting in ['role', 'rolle']:

            if not change:

                desc += '**Rolle zum Schreiben** :keyboard:\n\n'

                desc += f'**Aktuelle Rolle:** {self.settings["role"].name}\n'

                desc += '**Einstellung ändern:** `ehre settings role <NeueRolle>`\n'
                desc += '**Gültige Einstellungen:** Jede Rolle auf diesem Server\n'

                desc += '**Info:** Diese Rolle muss jedes Mitglied haben, um in allen Textchannels schreiben zu können. Diese Einstellung wird nur benötigt, ' \
                        'wenn Anti-Spam aktiviert ist, da der Bot im Falle eines Spamangriffs dem Spamer die Rolle entzieht und dieser somit nicht mehr schreiben kann. ' \
                        'Damit das funktioniert muss ein Serveradmin in jedem Textchannel einstellen, dass nur Personen mit dieser Rolle Nachrichten senden können.'

            else:

                if get(self.guild_obj.roles, name=change):

                    new_role = get(self.guild_obj.roles, name=change)
                    self.settings["role"] = new_role

                    desc += f':white_check_mark: Role zum Schreiben in allen Textchannels auf **{change}** gesetzt!'

                else:

                    desc += f':x: Die Rolle **{change}** gibts auf diesem Server nicht. Wenn du die Role ändern möchtest, solltest du eine vorhandene Rolle nehmen!'

        elif setting in ['vote', 'votetime', 'votum']:

            if not change:

                desc += '**Abstimmungszeit** :ballot_box:\n\n'

                desc += f'**Aktuelle Zeit:** {self.settings["vote_time"]}min\n'
                desc += f'**Mindesbeteiligung für Abstimmungen:** {self.settings["vote_threshold"]} Personen\n'

                desc += '**Einstellung ändern:** `ehre settings vote <NeueZeit>`\n'
                desc += '**Gültige Einstellungen:** Zeit in Minuten als Ganzzahl zwischen 1 und 1440 (24 Stunden)\n'

                desc += '**Info:** Mit dieser Einstellung kannst du festlegen, wie lange eine Abstimmung laufen soll, bevor sie ausgewertet wird.' \
                        ' Die Anzahl der Personen, die an einer Abstimmung teilgenommen haben müssen, wird automatisch anhand der Größe des Servers durch den' \
                        ' Bot festgelegt und kann _nicht manuell_ eingestellt werden!\n'

            else:
                try:

                    change = int(change)
                    if change < 1 or change > 1440:

                        desc += ':x: Bitte gib die Zeit in Minuten als Ganzzahl zwischen 1 und 1440 (24 Stunden) an!'

                    else:

                        self.settings["vote_time"] = change
                        desc += f':white_check_mark: Zeit pro Abstimmung auf **{change}** Minuten gesetzt!'

                except:

                    desc += ':x: Bitte gib die Zeit in Minuten als Ganzzahl zwischen 1 und 1440 (24 Stunden) an!'

        elif setting in ['antispam', 'anti-spam']:

            if not change:

                desc += '**Antispam** :zipper_mouth:\n\n'

                desc += f'**Status:** {":white_check_mark:" if self.settings["anti_spam"] == "on" else ":x:"}\n'
                desc += f'**Blokierung fürs Spamen:** {self.settings["spam_block_time"]}min\n'

                desc += '**Einstellung ändern:** `ehre settings antispam <NeueZeit>`\n'
                desc += '**Gültige Einstellungen:** `on`; `off`; Zeit in Minuten als Ganzzahl zwischen 1 und 1440 (24 Stunden)\n'

                desc += '**Info:** In den Einstellungen des Antispam kann festgelegt werden, ob spaming verhindert werden soll oder nicht, und wenn ja, wie lange eine Person fürs spamen' \
                        ' von der Teilnahme am Serverleben ausgeschlossen wird.\n'

            elif change == 'on':

                if self.settings["anti_spam"] == "off":

                    desc += f':white_check_mark: Nervensägen übernehme ich ab jetzt... :smirk:'

                else:

                    desc += f':x: Antispam ist bereits eingeschaltet!'

            elif change == 'off':

                if self.settings["anti_spam"] == "on":

                    desc += f':white_check_mark: Störenfriede ab sofort wieder zugelassen... :rolling_eyes:'

                else:

                    desc += f':x: Antispam ist bereits ausgeschaltet!'

            else:
                try:

                    change = int(change)
                    if change < 1 or change > 1440:

                        desc += ':x: Bitte gib die Zeit in Minuten als Ganzzahl zwischen 1 und 1440 (24 Stunden) an!'

                    else:

                        self.settings["spam_block_time"] = change
                        desc += f':white_check_mark: Zeit für Spaming auf **{change}** Minuten gesetzt!'

                except:

                    desc += ':x: Bitte gib die Zeit in Minuten als Ganzzahl zwischen 1 und 1440 (24 Stunden) an!'

        return desc


    def help(self, mode, member):

        member = self.members[member]
        desc = ''

        if not mode:

            desc += '\n\n**General Commands**'

            # HELP COMMAND
            desc += '\n\n**__help__**\n' # Command name
            desc += '\nSyntax: `ehre help <command>`'  # Syntax
            desc += '\nAliases: `help`' # Aliases
            desc += '\nInfo: Zeigt Hilfe für command.' # Short description of command

            # STATS COMMAND
            desc += '\n\n**__stats__**\n'  # Command name
            desc += '\nSyntax: `ehre stats`'  # Syntax
            desc += '\nAliases: `stats`, `statistics`' # Aliases
            desc += '\nInfo: Zeigt allgemeine Statistiken des Servers.'  # Short description of command

            desc += '\n\n**Member Commands**'

            # DONATION COMMAND
            desc += '\n\n**__donate__**\n'  # Command name
            desc += '\nSyntax: `ehre donate <member>`'  # Syntax
            desc += '\nAliases: `donate`' # Aliases
            desc += '\nInfo: Tägliche Spende an <member> vergeben.'  # Short description of command

            # DONATIONS COMMAND
            desc += '\n\n**__donations__**\n'  # Command name
            desc += '\nSyntax: `ehre donations`'  # Syntax
            desc += '\nAliases: `donations`' # Aliases
            desc += '\nInfo: Zeigt, wer gespendet hat und wer nicht.'  # Short description of command

            # VOTE COMMAND
            desc += '\n\n**__vote__**\n'  # Command name
            desc += '\nSyntax: `ehre vote <member> <ehre> <grund>`'  # Syntax
            desc += '\nAliases: `vote`, `votum`' # Aliases
            desc += '\nInfo: Erstellt ein Votum für diese Person.'  # Short description of command

            desc += '\n\n**Admin Commands**'

            # SETTINGS COMMAND
            desc += '\n\n**__settings__**\n'  # Command name
            desc += '\nSyntax: `ehre settings <einstellung> <option>`'  # Syntax
            desc += '\nAliases: `settings`'  # Aliases
            desc += '\nInfo: Zeigt und ändert Einstellungen des Servers.'  # Short description of command

            desc += '\n\nFür genauere Informationen zu einem bestimmten Command gib einfach `ehre help <command>` ein!'


        elif mode == 'help':

            desc += 'Wirklich witzig...'
            member.transaction(-10, 'Wollte witzig sein')

        elif mode == 'stats':

            desc += '**__stats__**\n'
            desc += '\n**Syntax:** `ehre stats`'  # Syntax
            desc += '\n**Aliases:** `stats`, `statistics`' # Aliases
            desc += '\n**Ausführbar von:** Allen' # Who is able to run it
            desc += '\n**Beschreibung:**\n Dieser Befehl gibt dir einen Überblick über die Statistiken des Servers. ' \
                    'Dazu zählt zum Beispiel, wer das ehrenhafteste Mitglied und wer der ehrenloseste ist, aber auch, ' \
                    'wieviel Ehre jedes Mitglied im Durchschnitt hat.'

        elif mode == 'donate':

            desc += '**__donate__**\n'
            desc += '\n**Syntax:** `ehre donate <member>`'  # Syntax
            desc += '\n**Aliases:** `donate`'  # Aliases
            desc += '\n**Ausführbar von:** Allen'  # Who is able to run it
            desc += '\n**Beschreibung:**\n Mit dem `donate` Befehl kann jedes Mitglied einmal pro Tag einem **anderen** Mitglied ' \
                    'seiner Wahl 10 Ehre spenden (diese wird nicht vom eigenen Konto abgezogen).'
            desc += '\n**Optionen:**\n `<member>`: Das Mitglied, an welches die Ehre gehen soll.'

        elif mode == 'donations':

            desc += '**__donations__**\n'
            desc += '\n**Syntax:** `ehre donations`'  # Syntax
            desc += '\n**Aliases:** `donations`'  # Aliases
            desc += '\n**Ausführbar von:** Allen'  # Who is able to run it
            desc += '\n**Beschreibung:**\n Zeigt, wieviele Mitglieder heute schon gespendet haben und wieviele (noch) nicht.'

        elif mode == 'settings':

            desc += '**__settings__**\n'
            desc += '\n**Syntax:** `ehre settings <einstellung> <neuerWert>`'  # Syntax
            desc += '\n**Aliases:** `settings`'  # Aliases
            desc += '\n**Ausführbar von:** Admins'  # Who is able to run it
            desc += '\n**Beschreibung:**\n Hierüber können die Servereinstellungen von Ehrenbot für den Server geändert werden. Um alle Einstellungen anzuzeigen ' \
                    'einfach `ehre settings` ohne jeglichen Parameter eingeben. Detailierte Informationen (u.a. wie du sie änderst) erhältst du, indem du `ehre settings ' \
                    '<einstellung>` eingibst, wenn du noch `<neuerWert>` angibst, änderst du die Einstellung auf diesen Wert.\n**Hinweis:** Manche Einstellungen werden automatisch ' \
                    'vom Bot angepasst und können nicht manuell eingestellt werden!'
            desc += '\n**Optionen:**\n `<settings>`: Die Einstellung, die du dir ansehen/die du ändern möchtest. `<neuerWert>`: Der Wert, auf den du die Einstellung setzen willst.'

        elif mode == 'vote':

            desc += '**__vote__**\n'
            desc += '\n**Syntax:** `ehre vote <member> <ehre> <grund>`'  # Syntax
            desc += '\n**Aliases:** `vote`, `votum`'  # Aliases
            desc += '\n**Ausführbar von:** Allen'  # Who is able to run it
            desc += '\n**Beschreibung:**\n Mit `vote` kannst du eine Abstimmung starten, in welcher es darum geht, dem von dir' \
                    ' angegebenen Mitglied aus einem von dir gennanten Grund Ehre hinzuzufügen oder abzuziehen. Diese Abstimmung ' \
                    'läuft dann eine bestimmte Zeit lang (welche sich in den Einstellungen des Servers verändern lässt) und wird nach ' \
                    'Ablauf dieser Zeitspanne automatisch ausgewertet. Damit die Abstimmung als erfolgreich gillt, müssen\n' \
                    '1. eine Mindestanzahl von Mitgliedern daran teil genommen haben.\n' \
                    '2. mehr Mitglieder dafür als dagegen gestimmt haben :scream:'
            desc += '\n**Optionen:**\n `<member>`: Das Mitglied, dessen Ehre erhöht oder verringert werden soll\n' \
                    '`<ehre>`: Ganzzahl, um die die Ehre erhöht werden soll (Minuszahl für Abzug).\n' \
                    '`<grund>`: Der Grund, mit welchem die veränderung der Ehre gerechtfertigt wird.`'

        else:

            desc += 'Unbekannter befehl, probier `ehre help` für eine Liste von Befehlen.'

        return discord.Embed(title='Help', description=desc, colour=random.randint(0, 16777215))



    def get_stats(self):

        member_count = sum(1 if not m.bot else 0 for m in self.guild_obj.members)
        stats = f':busts_in_silhouette: Members: **{member_count}** (ohne Bots)\n '

        max_ehre_usr = min_ehre_usr = list(self.members.values())[0].name
        max_ehre = min_ehre = all_ehre = list(self.members.values())[0].balance
        for member in list(self.members.values())[1:]:

            ehre = member.balance
            if ehre < min_ehre:

                min_ehre = ehre
                min_ehre_usr = member.name

            elif ehre > max_ehre:

                max_ehre = ehre
                max_ehre_usr = member.name

            all_ehre += ehre


        avg_ehre = int(all_ehre / member_count)
        stats += f':money_mouth: Ehrenhaftestes Mitglied: **{max_ehre_usr}**, **{max_ehre}** Ehre\n:shit: Ehrenlosester Kek: **{min_ehre_usr}**, **{min_ehre}** Ehre\n:scales: Durchschnittliche Ehre: **{avg_ehre}** Ehre'

        stats += f'\n\nOwner: **{self.guild_obj.owner.display_name}** :crown:'

        return stats

    async def donate(self, ctx, to_member):

        member = self.members[ctx.author.id]
        to_member = self.members[to_member]
        if not member.donated:

            if not member == to_member:

                self.transaction(to_member, 10, 'tägliche Spende')
                member.donated = True

                await ctx.send(f'**{member.name}** -> :money_with_wings: -> **{to_member.name}**')

            else:

                await ctx.send(f'Wie aussieht haben wir hier einen Egoisten...\n-10 Ehre dafür :grimacing:')
                member.transaction(-10, 'Egoistisches Verhalten')

        else:

            await ctx.send(f'Du hast heute schon Ehre verteilt, **{member.name}**!')

    async def member_ehre_history(self, ctx, mode):

        member = self.members[ctx.author.id]
        emb = discord.Embed(title=f'Accountverlauf von {member.name}', description=member.transaction_hist, colour=random.randint(0, 16777215))
        if mode in ['private', 'Privat', 'privat']:

            await ctx.author.send(embed=emb)

        else:

            await ctx.send(embed=emb)

    async def create_vote(self, ctx, to_member: int, amount, reason):

        vote = await Vote.create(ctx, self, to_member, amount, reason)
        if not vote == None:
            self.votes[str(ctx.author.id)] = vote
