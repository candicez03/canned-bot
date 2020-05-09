import os
import random

import discord
import logging
from tinydb import TinyDB, Query

logging.basicConfig()
TOKEN = os.getenv('DISCORD_TOKEN')
DEFAULT_PREFIX = 'uwu'
activities = {
    discord.ActivityType.playing: 'playing',
    discord.ActivityType.streaming: 'streaming',
    discord.ActivityType.listening: 'listening',
    discord.ActivityType.watching: 'watching',
}

commands = {
    'be my friend': 'Friendship!(allows me to react to your messages, activities, status, etc.)',
    'am i your friend': 'Checks whether you are a friend of mine or not! :P',
    'commands': 'Displays all available commands',
    'set default channel': "Sets the default channel to the current channel. I will react to my friends' updates in this channel",
    'set emoji freq': 'A number from 0-100 that determines how often I will send an emoji when replying to your messages. Remember, you must make friends with me first ;)',
    'set prefix': 'Sets my prefix in this server',
    'set rep freq': 'A number from 0-100 that determines how often I will reply to your messages. Remember, you must make friends with me first ;)',
    'shut up': 'End friendship...(disallows me to react to your messages, activities, status, etc.)',
    'reset prefix': 'Resets my prefix in this server to its default. You can also mention me and shout out help to reset ;p',
}

commandEmbed = discord.Embed(title="Help", description="Candy is enslaving me", color=0xcf80ff)
commandEmbed.set_thumbnail(url="https://cdn.discordapp.com/avatars/707779897807863838/55fa08b1f53164d5f6eb1b8bfffc5faf.png")
commandEmbed.set_footer(text="please help candy is making me suffer please save me oh heck oh frick she's comi-")
for command, description in commands:
    commandEmbed.add_field(name=command, value=description, inline=False)

client = discord.Client()
userDB = TinyDB('userData.json')
guildDB = TinyDB('guildData.json')
emojiDB = TinyDB('emojiData.json')
# to do: when finding default channel find the first text channel that it has perm to send msgs
#       instead of just the first txtchan of all txtchans


def isFriendWithUser(userId):
    myQuery = Query()
    return len(userDB.search((myQuery.id == userId) & (Query().is_friend == True))) > 0


def getGuildUpdater(guildId):
    def updateGuild(record):
        guildDB.update(record, Query().id == guildId)
    return updateGuild


def getUserUpdater(userId):
    def updateUser(record):
        userDB.update(record, Query().id == userId)
    return updateUser


def initGuild(guildId, guildDefaultChannelId, guildPrefix=DEFAULT_PREFIX):
    guildDB.insert({
        'id': guildId,
        'default_channel_id': guildDefaultChannelId,
        'prefix': guildPrefix,
    })
    return True


def initUser(userId, userIsFriend=False, userRepFreq=50):
    global userDB
    userDB.insert({
        'id': userId,
        'is_friend': userIsFriend,
        'reply_frequency': userRepFreq,
    })
    return True


async def handleCommand(msg):
    reply = msg.channel.send
    updateGuild = getGuildUpdater(msg.guild.id)
    updateUser = getUserUpdater(msg.author.id)
    myQuery = Query()

    curPrefix = guildDB.search(myQuery.id == msg.guild.id)[0]['prefix']
    if client.user.mentioned_in(msg):
        if 'help' in msg.content:
            updateGuild({'prefix': DEFAULT_PREFIX})
            await reply(f'Prefix reset to {DEFAULT_PREFIX}')
        elif 'greet' in msg.content:
            strToGreet = ""
            for member in msg.guild.members:
                if member != client.user and str(member.status) == 'online':
                    roleStrs = set([role.name for role in member.roles])
                    if 'bot' in roleStrs:
                        strToGreet += f'Hi my fellow bot {member.name}\n'
                    elif isFriendWithUser(member.id):
                        strToGreet += f'Hi my friend {member.name} :p\n'
                    else:
                        strToGreet += f'Hello {member.name}\n'
            await reply(strToGreet)
        else:
            await reply(f'My prefix is {curPrefix}\nUse `{curPrefix} commands` to check available commands')
        return

    if not msg.content.startswith(curPrefix):
        return

    commandStr = msg.content.lower()[len(curPrefix)+1:]  # remove the prefix

    if commandStr.startswith('be my friend'):
        updateUser({'is_friend': True})
        await reply('Sure! I hope you dont find me too annoying :P')

    elif commandStr.startswith('shut up'):
        if not isFriendWithUser(msg.author.id):
            await reply("...but I'm not even ur friend ;-;")
            return
        print(userDB.search(myQuery.id == msg.author.id))
        updateUser({'is_friend': False})
        await reply('awww okay ://')

    elif commandStr.startswith('change prefix'):
        newPrefix = commandStr[len('change prefix')+1:]
        if len(newPrefix) == 0:
            await reply('invalid prefix')
            return
        updateGuild({'prefix': newPrefix})
        await reply(f'prefix changed to {newPrefix}')

    elif commandStr.startswith('set default channel'):
        updateGuild({'default_channel_id': msg.channel.id})
        await reply('default channel set to here :P')

    elif commandStr.startswith('reset prefix'):
        updateGuild({'prefix': DEFAULT_PREFIX})
        await reply(f'Prefix reset to {DEFAULT_PREFIX}')

    elif commandStr.startswith('set rep freq'):
        if not isFriendWithUser(msg.author.id):
            await reply('Remember, you must make friends with me first ;)')
            return
        freq = commandStr[len('set rep freq')+1:]
        try:
            freq = float(freq)
            if freq < 0 or freq > 100:
                raise ValueError
            updateUser({'reply_frequency': freq})
            await reply(f'reply frequency set to {freq}')
        except ValueError:  # float(x) failed or result was out of range
            await reply('Invalid :( please enter a number from 0-100')

    elif commandStr.startswith('set emoji freq'):
        await reply('developing...')

    elif commandStr.startswith('am i your friend'):
        if isFriendWithUser(msg.author.id):
            await reply('yes! ;p')
        else:
            await reply('umm no...;-; why not make friends with me?')

    elif commandStr.startswith('commands'):
        await reply(embed=commandEmbed)
        # output = f'```\n{client.user.name} Commands:\n\n'
        # for command in commands:
        #     output += f'- {command}: {commands[command]}\n\n'
        # output += '```'
        # await reply(output)


@client.event
async def on_ready():
    print(f'logged in as {client.user}')
    myQuery = Query()
    for guild in client.guilds:
        # if guild.id != 678357164510806046: continue
        if len(guildDB.search(myQuery.id == guild.id)) == 0:
            initGuild(guild.id, guild.text_channels[0].id)
        for member in guild.members:
            if (member != client.user
                    and len(userDB.search(myQuery.id == member.id)) == 0):
                initUser(member.id)


@client.event
async def on_message(msg):
    print(f'{msg.author.name} ({msg.author.id}): {msg.content}')

    if msg.author == client.user:
        return
    myQuery = Query()

    # despacito
    if msg.author.id == 268517328935845915:  # kevoon
        if msg.guild.id == 670687159866490911:  # typescript fan club, emoji 14
            for emoji in msg.guild.emojis:
                if emoji.name == 'emoji_14':
                    await msg.add_reaction(emoji)
        else:
            await msg.add_reaction('☺️')  # relaxed

    handleCommand(msg)

    if isFriendWithUser(msg.author.id):
        if random.random()*100 < userDB.search(myQuery.id == msg.author.id)[0]['reply_frequency']:
            reply = 'no u'
            # if random.random()*100 < emoji_freq: reply += ' ' + random.choice(text_emojis)
            await msg.channel.send(reply)


@client.event
async def on_member_update(before, after):
    if before == client.user:
        return
    myQuery = Query()
    if not isFriendWithUser(before.id):
        return
    channelId = guildDB.search(myQuery.id == before.guild.id)[0]["default_channel_id"]
    channelToSend = before.guild.get_channel(channelId)
    nickname = after.nick
    if after.nick is None:
        nickname = after.name
    if before.nick != after.nick:
        await channelToSend.send(f'Nice nickname {nickname}')

    elif before.status != after.status:
        if str(after.status) == 'online':
            await channelToSend.send(f'Wow {nickname} has come online')
        elif str(after.status) == 'offline':
            await channelToSend.send(f'Oof {nickname} is gone')
        elif str(after.status) == 'dnd':
            await channelToSend.send(f'Nice dnd {nickname}')

    elif before.activity != after.activity:
        text = ' '
        if after.activity is None:
            if before.activity.type in activities:
                text = f'Hmm {nickname} has stopped {activities[before.activity.type]} {before.activity.name}'
        else:
            if after.activity.type in activities:
                text = f'Woah {nickname} is {activities[after.activity.type]} {after.activity.name}'
            else:
                text = f'nice custom status {nickname}'
        await channelToSend.send(text)


@client.event
async def on_message_delete(msg):
    await msg.channel.send(f'did someone just delete a message :eyes:\n> {msg.content}\n<@{msg.author.id}>')


@client.event
async def on_message_edit(before, after):
    await after.channel.send(f"nice edited\n||{before.content}||")


@client.event
async def on_guild_channel_delete(channel):
    myQuery = Query()
    if guildDB.search(myQuery.id == channel.guild.id)[0]['default_channel'] == channel.id:
        guildDB.update(
            {'default_channel': channel.guild.text_channels[0].id}, myQuery.id == channel.guild.id
        )
        await channel.guild.text_channels[0].send('aww :(( My default channel in this server has disappeared! Please set a new default channel for me or I will use this channel from now on ;p')


@client.event
async def on_member_join(member):
    myQuery = Query()
    if len(userDB.search(myQuery.id == member.id)) == 0:
        initUser(member.id)


@client.event
async def on_guild_join(guild):
    initGuild(guild.id, guild.text_channels[0].id)
    await guild.text_channels[0].send("Hi, I'm canned bot and I hope to make some friends here ;p")


@client.event
async def on_guild_remove(guild):
    print(f"removed from guild {guild.name}")
    guildDB.remove(Query().id == guild.id)

client.run(TOKEN)
