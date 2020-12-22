import datetime
import json

admin = 'ADMINNAME#ADMINTAG'


def log(info, timestamp=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), server='SYSTEM'):
    info = f'[{timestamp}] ({server}) {info}\n'
    print(info.replace('\n', ''))
    with open(f'guild_data/_default/logs/{datetime.datetime.now().strftime("%d_%m_%Y")}.log', 'a') as f:
        f.write(info)


def has_permission(author, guild, level):
    author_level = 0

    if str(author) == admin:

        author_level = 3

    elif author == str(guild.owner):

        author_level = 2

    elif author.guild_permissions.administrator:

        author_level = 1

    if author_level >= level:
        return True
    else:
        return False

def load_config():
    with open(f'config.json', 'r') as conf:
        configs = json.load(conf)
    return configs