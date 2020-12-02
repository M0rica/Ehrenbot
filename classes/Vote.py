import datetime
import asyncio
import discord
import random

class Vote:

    def __init__(self, time, to_member, amount, reason, message, message_channel):


        self.time = time
        self.to_member = to_member
        self.amount = amount
        self.reason = reason
        self.message = message
        self.message_channel = message_channel

        self.created_at = datetime.datetime.now().strftime('%H%M')

    def to_dict(self):

        return {
         "time": self.time,
         "to_member": self.to_member,
         "amount": self.amount,
         "reason": self.reason,
         "message": self.message,
         "message_channel": self.message_channel,
         "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):

        return Vote(data["time"], data["to_member"], data["amount"], data["reason"], data["message"], data["message_channel"], data["created_at"])

    @staticmethod
    async def create(ctx, server, to_member, amount, reason):

        member = server.members[ctx.author.id]

        if not member.has_vote:

            if to_member in server.members:

                to_member = server.members[to_member]

                if not member == to_member:

                    try:

                        amount = int(amount)

                        emb = discord.Embed(title="Ehrenvotum :ballot_box:", colour=random.randint(0, 16777215))
                        votum_description = f'{reason} \n\n:money_with_wings:**{to_member.name}** würde **{amount}** Ehre bekommen.\n\nUm abzustimmen, reagiere einfach mit\n:thumbsup: ' \
                                            f'Daumen hoch, wenn du der Meinung bist, dass dieser Move gerechtfertigt ist,\noder mit nem\n:thumbsdown: Dauem nach unten, wenn du denkst, ' \
                                            f'dass die Eher der Person auf dem gleichen niveau bleiben sollte wie bisher.\n\nWer dafür **und** dagegen stimmt wird gekreuzigt!'
                        emb.add_field(name=f'von **{member.name}**:', value=votum_description)
                        message = await ctx.send(embed=emb)
                        reactions = ['\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}']
                        for reac in reactions:
                            await message.add_reaction(reac)

                        member.has_vote = True

                        server.log(f'{member.name} created a vote')

                        return Vote(server.settings["vote_time"], to_member.member_id, amount, reason, message.id, message.channel.id)

                    except:

                        emb = discord.Embed(title='Ehrenvotum :ballot_box:',
                                            description=f'Es ist nicht möglich, ein Votum zu erstellen, bei dem es nicht um Ehre geht, **{member.name}**!',
                                            colour=random.randint(0, 16777215))
                        await ctx.send(embed=emb)


                else:

                    emb = discord.Embed(title='Ehrenvotum :ballot_box:',
                                        description=f'**{member.name}**, du kannst kein Votum für dich selbst einrichten! :rolling_eyes:',
                                        colour=random.randint(0, 16777215))
                    await ctx.send(embed=emb)

            else:

                emb = discord.Embed(title='Ehrenvotum :ballot_box:',
                                    description=f'Dieser Benutzer ist entweder nicht hier auf dem Server oder existiert nicht, **{member.name}** :expressionless:',
                                    colour=random.randint(0, 16777215))
                await ctx.send(embed=emb)

        else:

            emb = discord.Embed(title='Ehrenvotum :ballot_box:',
                                description=f'Wolltest wohl lustig sein und mehrere Abstimmungen gleichzeitg laufen lass, was? So nicht, freundchen!',
                                colour=random.randint(0, 16777215))
            await ctx.send(embed=emb)
            member.transaction(-5, 'Versuch, mehrere Abstimmungen gleichzeitg zu erstellen')

        return None


    async def eval(self, server, channel, vote_threshold, member, to_member):


        new_msg: discord.Message
        new_msg = await channel.fetch_message(self.message)

        reaction_list = new_msg.reactions
        users_reacted = []
        for reaction in reaction_list:

            if reaction.emoji == '\N{THUMBS UP SIGN}':

                users_reacted = await reaction.users().flatten()
                positive = reaction.count

            elif reaction.emoji == '\N{THUMBS DOWN SIGN}':

                async for user in reaction.users():
                    if user in users_reacted:
                        if not user.bot:
                            server.transaction(server.members[user.id], -15, 'Symbolische Kreuzigung wie angekündigt')

                negative = reaction.count

        score = positive - negative
        all_score = round((positive + negative) / 2, 0)

        if score >= vote_threshold:

            self.transaction(to_member, int(self.amount), f'durch Votum: {self.reason}')

            answer = f":white_check_mark: Die Abstimmung von {member.name} war Erfolgreich! :partying_face:\n**{to_member.name}'s** Ehre wurde deswegen um **{self.amount}** verändert."
            col = 2081352

        elif score < vote_threshold and all_score > vote_threshold:

            answer = f':x: Die Abstimmung von {member.name} wurde Abgelehnt, somit bleib die Ehre von {to_member.name} unverändert.'
            col = 14359563

        elif score < vote_threshold and all_score <= vote_threshold:

            answer = f':x: Die Abstimmung von {member.name} ist gescheitert, da sie niemanden interessiert hat. :sleeping:'
            col = 14359563

        emb = discord.Embed(title='Auswertung des Votums', colour=col)
        emb.add_field(name=f"von **{member.name}** für **{to_member.name}**:", value=answer)



