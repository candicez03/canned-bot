import os
import discord
import logging
from tinydb import TinyDB, Query

logging.basicConfig()
TOKEN = os.getenv("DISCORD_TOKEN")
DEFAULT_PREFIX = "uwu"
activities = {discord.ActivityType.playing: "playing",\
              discord.ActivityType.streaming: "streaming",\
              discord.ActivityType.listening: "listening",\
              discord.ActivityType.watching: "watching",}

commands = {"be my friend": "Friendship!(allows the bot to react to your messages, activities, status, etc.)",\
            "shut up": "Disallows the bot to react to your messages, activities, status, etc.",\
            "change prefix": "Changes the prefix of the bot",\
            "reset prefix": "Resets the prefix of the bot to its default. You can also mention the bot and shout out help to reset ;p",\
            "set default channel": "Sets the default channel to the current channel. The bot will react to its friends' updates in this channel",\
            "commands": "Displays all available commands"}

client = discord.Client()
userDB = TinyDB('userData.json')
guildDB = TinyDB('guildData.json')

@client.event
async def on_ready():
  print('logged in as {0.user}'.format(client))
  for guild in client.guilds:
    #if guild.id != 678357164510806046: continue
    if len(guildDB.search(Query().id == guild.id)) == 0:
      guildDB.insert({"id": guild.id, "default_channel_id": guild.text_channels[0].id, "prefix": DEFAULT_PREFIX})
    for member in guild.members:
      if member != client.user and len(userDB.search(Query().id == member.id)) == 0:
        userDB.insert({"id": member.id, "is_friend": False})
  

@client.event
async def on_message(message):
  print(message.content)
  if message.author == client.user:
    return

  #despacito
  if message.author.id == 268517328935845915: #kevoon
    if message.guild.id == 670687159866490911:#typescript fan club, emoji 14
      for emoji in message.guild.emojis:
        if emoji.name == 'emoji_14':
          await message.add_reaction(emoji) 
    else: await message.add_reaction("☺️") #relaxed
  
  #commands
  curPrefix = guildDB.search(Query().id == message.guild.id)[0]['prefix']
  
  if client.user.mentioned_in(message):
    if "help" in message.content:
      guildDB.update({'prefix': DEFAULT_PREFIX}, Query().id == message.guild.id)
      await message.channel.send("Prefix reset to "+DEFAULT_PREFIX)
    elif "greet" in message.content:
      for member in message.guild.members:
        if member != client.user and str(member.status) == "online":
          roleStrs = [role.name for role in member.roles]
          if "bot" in roleStrs:
            await message.channel.send("Hi my fellow bot " + member.name)
          elif len(userDB.search(Query().id == message.author.id and Query().is_friend == True)) > 0:
            await message.channel.send("Hi my friend " + member.name + " :p")
          else:
            await message.channel.send("Hello " + member.name)
    else:
      await message.channel.send("My prefix is " + curPrefix + "\nUse `" + curPrefix + " commands` to see available commands")
    
  elif message.content.startswith(curPrefix):
    lowerCaseStr = message.content.lower()
    for key in commands:
      if key in lowerCaseStr:
        print("command detected")
        if key == "be my friend":
          print(userDB.search(Query().id == message.author.id))
          userDB.update({'is_friend': True}, Query().id == message.author.id)
          await message.channel.send("Sure! I hope you dont find me too annoying :P")

        elif key == "shut up":
          if len(userDB.search(Query().id == message.author.id and Query().is_friend == True)) == 0:
            await message.channel.send("...but I haven't even said anything :((")
          else:
            userDB.update({'is_friend': False}, Query().id == message.author.id)
            await message.channel.send("awww okay ://")

        elif key == "change prefix":
          if len(message.content) <= len(curPrefix)+len(" change prefix"):
            await message.channel.send("invalid prefix")
          else:
            newPrefix = lowerCaseStr[(lowerCaseStr.index("change prefix")+len("change prefix")+1):]
            guildDB.update({'prefix': newPrefix}, Query().id == message.guild.id)
            await message.channel.send("prefix changed to " + newPrefix)

        elif key == "set default channel":
          guildDB.update({'default_channel_id': message.channel.id}, Query().id == message.guild.id)
          await message.channel.send("default channel set to here :P")

        elif key == "reset prefix":
          guildDB.update({'prefix': DEFAULT_PREFIX}, Query().id == message.guild.id)
          await message.channel.send("Prefix reset to "+DEFAULT_PREFIX)

        elif key == "commands":
          output = "```\n" + client.user.name + " Commands:\n\n"
          for command in commands:
            output += '- ' + command + ': ' + commands[command] + '\n\n'
          output += "```"
          await message.channel.send(output)
        break

@client.event
async def on_member_update(before, after):
  if before == client.user:
    return
  if len(userDB.search(Query().id == before.id and Query().is_friend == True)) == 0:
    return
  channelId = guildDB.search(Query().id == before.guild.id)[0]["default_channel_id"]
  channelToSend = before.guild.get_channel(channelId)
  nickname = after.nick
  if after.nick == None: nickname = after.name
  if before.nick != after.nick:
    await channelToSend.send("Nice nickname " + nickname)

  elif before.status != after.status:
    if str(after.status) == "online":
      await channelToSend.send("Wow " + nickname + " has come online")
    elif str(after.status) == "offline":
      await channelToSend.send("Oof " + nickname + " is gone")
    elif str(after.status) == "dnd":
      await channelToSend.send("Nice dnd " + nickname)
  
  elif before.activity != after.activity:
    text = ' '
    if after.activity == None:
      if before.activity.type in activities:
        text = "Hmm " + nickname + " has stopped " + activities[before.activity.type] + ' ' + before.activity.name
    else:
      if after.activity.type in activities:
        text = "Woah " + nickname + " is " + activities[after.activity.type] + ' ' + after.activity.name
      else: text = "nice custom status " + nickname
    await channelToSend.send(text)

@client.event
async def on_message_delete(message):
  await message.channel.send('did someone just delete a message :eyes:\n' + \
                              '> ' + message.content + '\n<@' + str(message.author.id) + '>')

@client.event
async def on_message_edit(before, after):
  await after.channel.send("nice edited\n||" + before.content + "||")

client.run(TOKEN)