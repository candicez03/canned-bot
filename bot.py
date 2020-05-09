import os
import discord
import logging
import random
from tinydb import TinyDB, Query

logging.basicConfig()
TOKEN = os.getenv('DISCORD_TOKEN')
DEFAULT_PREFIX = 'uwu'
activities = {discord.ActivityType.playing: 'playing',\
              discord.ActivityType.streaming: 'streaming',\
              discord.ActivityType.listening: 'listening',\
              discord.ActivityType.watching: 'watching'}

commands = {'be my friend': 'Friendship!(allows me to react to your messages, activities, status, etc.)',\
            'am i your friend': 'Checks whether you are a friend of mine or not! :P',\
            'commands': 'Displays all available commands',\
            'set default channel': "Sets the default channel to the current channel. I will react to my friends' updates in this channel",\
            'set emoji freq': 'A number from 0-100 that determines how often I will send an emoji when replying to your messages. Remember, you must make friends with me first ;)',\
            'set prefix': 'Sets my prefix in this server',\
            'set rep freq': 'A number from 0-100 that determines how often I will reply to your messages. Remember, you must make friends with me first ;)',\
            'shut up': 'End friendship...(disallows me to react to your messages, activities, status, etc.)',\
            'reset prefix': 'Resets my prefix in this server to its default. You can also mention me and shout out help to reset ;p',\
            }

client = discord.Client()
userDB = TinyDB('userData.json')
guildDB = TinyDB('guildData.json')
emojiDB = TinyDB('emojiData.json')
#to do: when finding default channel find the first text channel that it has perm to send msgs
#       instead of just the first txtchan of all txtchans

def isFriendWithUser(userId):
  global userDB
  myQuery = Query()
  return len(userDB.search((myQuery.id == userId) & (Query().is_friend == True))) > 0

def initGuild(guildId, guildDefaultChannelId, guildPrefix=DEFAULT_PREFIX):
  global guildDB
  guildDB.insert({'id': guildId, 'default_channel_id': guildDefaultChannelId, 'prefix': guildPrefix})
  return True

def initUser(userId, userIsFriend=False, userRepFreq=50):
  global userDB
  userDB.insert({'id': userId, 'is_friend': userIsFriend, 'reply_frequency': userRepFreq})
  return True

@client.event
async def on_ready():
  print('logged in as {0.user}'.format(client))
  myQuery = Query()
  for guild in client.guilds:
    #if guild.id != 678357164510806046: continue
    if len(guildDB.search(myQuery.id == guild.id)) == 0:
      initGuild(guild.id, guild.text_channels[0].id)
    for member in guild.members:
      if member != client.user and len(userDB.search(myQuery.id == member.id)) == 0:
        initUser(member.id)
  

@client.event
async def on_message(message):
  print(message.author.name + ' (' + str(message.author.id) + '): ' + message.content)
  if message.author == client.user:
    return
  myQuery = Query()

  #despacito
  if message.author.id == 268517328935845915: #kevoon
    if message.guild.id == 670687159866490911: #typescript fan club, emoji 14
      for emoji in message.guild.emojis:
        if emoji.name == 'emoji_14':
          await message.add_reaction(emoji) 
    else: await message.add_reaction('☺️') #relaxed
  
  #commands
  curPrefix = guildDB.search(myQuery.id == message.guild.id)[0]['prefix']
  if client.user.mentioned_in(message):
    if 'help' in message.content:
      guildDB.update({'prefix': DEFAULT_PREFIX}, myQuery.id == message.guild.id)
      await message.channel.send('Prefix reset to '+DEFAULT_PREFIX)
    elif 'greet' in message.content:
      strToGreet = ""
      for member in message.guild.members:
        if member != client.user and str(member.status) == 'online':
          roleStrs = [role.name for role in member.roles]
          if 'bot' in roleStrs:
            strToGreet += 'Hi my fellow bot ' + member.name
          elif isFriendWithUser(member.id):
            strToGreet += 'Hi my friend ' + member.name + ' :p'
          else:
            strToGreet += 'Hello ' + member.name
          strToGreet += '\n'
      await message.channel.send(strToGreet)
    else:
      await message.channel.send('My prefix is ' + curPrefix + '\nUse `' + curPrefix + ' commands` to check available commands')
  
  elif message.content.startswith(curPrefix):
    lowerCaseStr = message.content.lower()
    for key in commands:
      if key in lowerCaseStr:
        if key == 'be my friend':
          userDB.update({'is_friend': True}, myQuery.id == message.author.id)
          await message.channel.send('Sure! I hope you dont find me too annoying :P')

        elif key == 'shut up':
          if not isFriendWithUser(message.author.id):
            await message.channel.send("...but I'm not even ur friend ;-;")
          else:
            print(userDB.search(myQuery.id==message.author.id))
            userDB.update({'is_friend': False}, myQuery.id == message.author.id)
            await message.channel.send('awww okay ://')

        elif key == 'change prefix':
          if len(message.content) <= len(curPrefix)+len(' change prefix'):
            await message.channel.send('invalid prefix')
          else:
            newPrefix = lowerCaseStr[(lowerCaseStr.index('change prefix')+len('change prefix')+1):]
            guildDB.update({'prefix': newPrefix}, myQuery.id == message.guild.id)
            await message.channel.send('prefix changed to ' + newPrefix)

        elif key == 'set default channel':
          guildDB.update({'default_channel_id': message.channel.id}, myQuery.id == message.guild.id)
          await message.channel.send('default channel set to here :P')

        elif key == 'reset prefix':
          guildDB.update({'prefix': DEFAULT_PREFIX}, myQuery.id == message.guild.id)
          await message.channel.send('Prefix reset to '+DEFAULT_PREFIX)

        elif key == 'set rep freq':
          if not isFriendWithUser(message.author.id):
            await message.channel.send('Remember, you must make friends with me first ;)')
          else:
            freq = lowerCaseStr[(lowerCaseStr.index('set rep freq')+len('set rep freq')+1):]
            try:
              freq = eval(freq)
              if 0 <= freq <= 100:
                userDB.update({'reply_frequency': freq}, myQuery.id == message.author.id)
                await message.channel.send('reply frequency set to '+str(freq))
              else: await message.channel.send('Invalid :( please enter a number from 0-100')
            except:
              await message.channel.send('Invalid :( please enter a number from 0-100')

        elif key == 'set emoji freq':
          await message.channel.send('developing...')

        elif key == 'am i your friend':
          if isFriendWithUser(message.author.id):
            await message.channel.send('yes! ;p')
          else: await message.channel.send('umm no...;-; why not make friends with me?')
        elif key == 'commands':
          output = '```\n' + client.user.name + ' Commands:\n\n'
          for command in commands:
            output += '- ' + command + ': ' + commands[command] + '\n\n'
          output += '```'
          await message.channel.send(output)
        break

  if isFriendWithUser(message.author.id):
    if random.random()*100 < userDB.search(myQuery.id == message.author.id)[0]['reply_frequency']:
      reply = 'no u'
      #if random.random()*100 < emoji_freq: reply += ' ' + random.choice(text_emojis)
      await message.channel.send(reply)

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
  if after.nick == None: nickname = after.name
  if before.nick != after.nick:
    await channelToSend.send('Nice nickname ' + nickname)

  elif before.status != after.status:
    if str(after.status) == 'online':
      await channelToSend.send('Wow ' + nickname + ' has come online')
    elif str(after.status) == 'offline':
      await channelToSend.send('Oof ' + nickname + ' is gone')
    elif str(after.status) == 'dnd':
      await channelToSend.send('Nice dnd ' + nickname)
  
  elif before.activity != after.activity:
    text = ' '
    if after.activity == None:
      if before.activity.type in activities:
        text = 'Hmm ' + nickname + ' has stopped ' + activities[before.activity.type] + ' ' + before.activity.name
    else:
      if after.activity.type in activities:
        text = 'Woah ' + nickname + ' is ' + activities[after.activity.type] + ' ' + after.activity.name
      else: text = 'nice custom status ' + nickname
    await channelToSend.send(text)

@client.event
async def on_message_delete(message):
  await message.channel.send('did someone just delete a message :eyes:\n' + \
                              '> ' + message.content + '\ndeleted by <@' + str(message.author.id) + '>')

@client.event
async def on_message_edit(before, after):
  await after.channel.send("nice edited\n||" + before.content + "||")

@client.event
async def on_guild_channel_delete(channel):
  myQuery = Query()
  if guildDB.search(myQuery.id == channel.guild.id)[0]['default_channel'] == channel.id:
    guildDB.update({'default_channel': channel.guild.text_channels[0].id}, myQuery.id == channel.guild.id)
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
  print("removed from guild " + guild.name)
  myQuery = Query()
  guildDB.remove(myQuery.id == guild.id)

client.run(TOKEN)