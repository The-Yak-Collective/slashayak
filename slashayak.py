## parts from here: https://gist.github.com/Rapptz/c4324f17a80c94776832430007ad40e6#slash-commands-and-context-menu-commands

    



from discord.ext import tasks, commands
import discord
import asyncio
import os
import re
import subprocess
import time
import datetime
from dotenv import load_dotenv

import logging


from discord_slashayak import * #including client and tree

HOME_DIR="/home/yak/robot/slashayak/"
USER_DIR="/home/yak/"

load_dotenv(USER_DIR+'.env')

@tree.command()
@app_commands.describe(echome='text to echo')
async def slashatest(interaction: discord.Interaction, echome: str):
    await interaction.response.send_message(f'{echome=}', ephemeral=True)

@client.event #needed since it takes time to connect to discord
async def on_ready(): 
    print("slashayak is up!")
    await tree.sync()
    return


discord_token=os.getenv('SLASHAYAK_DISCORD_KEY')
client.run(discord_token) 
