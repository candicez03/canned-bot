import discord

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