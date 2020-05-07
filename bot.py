import os
import discord
import logging
from config import *

class GuildData(object):
  def __init__(self, guild):
    self.guildPerm = dict()
    self.defultChannel = guild.text_channels[0]
  def setMember(self, member, perm=False):
    self.guildPerm[member] = perm
  def setDefultChannel(self, channel):
    self.defultChannel = channel
  def getPerm(self, member):
    return self.guildPerm[member]

def isFriend(guild, member):
  return guildsInfo[guild].getPerm(member)

logging.basicConfig()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()
prefix = DEFAULT_PREFIX
guildsInfo = dict()

@client.event
async def on_ready():
  print('logged in as {0.user}'.format(client))
  for guild in client.guilds:
    #if guild.id != 678357164510806046: continue
    gData = GuildData(guild)
    for member in guild.members:
      if member != client.user:
        gData.setMember(member)
        #if str(member.status) == 'online':
          #await gData.defultChannel.send('Hi '+member.name)
    guildsInfo[guild] = gData

@client.event
async def on_message(message):
  global prefix
  print(message.content)
  if message.author == client.user:
    return

  if message.author.id == 268517328935845915: #kevoon
    if message.guild.id == 670687159866490911:#typescript fan club, emoji 14
      for emoji in message.guild.emojis:
        if emoji.name == 'emoji_14':
          await message.add_reaction(emoji) 
    else: await message.add_reaction("☺️") #relaxed
  
  #commands
  if client.user.mentioned_in(message):
    if "help" in message.content:
      prefix = DEFAULT_PREFIX
      await message.channel.send("Prefix reset to "+DEFAULT_PREFIX)
    elif "greet" in message.content:
      for member in message.guild.members:
        if member != client.user and str(member.status) == "online":
          if message.author.bot:
            await message.channel.send("Hi my fellow bot " + member.name)
          elif isFriend(message.guild, message.author):
            await message.channel.send("Hi my friend " + member.name + " :p")
          else:
            await message.channel.send("Hello " + member.name)
    else:
      await message.channel.send("My prefix is " + prefix + "\nUse `" + prefix + " commands` to see available commands")
    

  elif message.content.startswith(prefix):
    lowerCaseStr = message.content.lower()
    for key in commands:
      if key in lowerCaseStr:
        if key == "be my friend":
          guildsInfo[message.guild].setMember(message.author, True)
          await message.channel.send("Sure! I hope you dont find me too annoying :P")

        elif key == "shut up":
          guildsInfo[message.guild].setMember(message.author, False)
          await message.channel.send("awww okay ://")

        elif key == "change prefix":
          if len(message.content) <= len(prefix)+len(" change prefix"):
            await message.channel.send("invalid prefix")
          else:
            prefix = lowerCaseStr[(lowerCaseStr.index("change prefix")+len("change prefix")+1):]
            await message.channel.send("prefix changed to " + prefix)

        elif key == "set default channel":
          guildsInfo[message.guild].setDefultChannel(message.channel)
          await message.channel.send("default channel set to here :P")

        elif key == "reset prefix":
          prefix = DEFAULT_PREFIX

        elif key == "commands":
          output = "```\n" + client.user.name + " Commands:\n\n"
          for command in commands:
            output += '- ' + command + ': ' + commands[command] + '\n\n'
          output += "```"
          await message.channel.send(output)
        break

@client.event
async def on_member_update(before, after):
  if before == client.user or (not guildsInfo[before.guild].getPerm(before)):
    return
  channelToSend = guildsInfo[after.guild].defultChannel
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