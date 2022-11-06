#separate files so we can split up robot between multiple files, if we want

import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.members = True
intents.messages=True
intents.message_content=True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

#maybe not bot but slash?
#bot = commands.Bot(command_prefix='$$', intents=intents)
#print("bot:",bot)
