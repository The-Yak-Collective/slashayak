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
@app_commands.describe(linktounfurl='the link, also from a thread, to unfurl. single link only, sorry. latter to add a whole thread, i guess')
async def tfurl(interaction: discord.Interaction, linktounfurl: str):

    message=interaction.message #there are actually cooler tools around interactions. for a later time...
    channel=interaction.channel
    url=linktounfurl #just for backwards compatibility and prevent need to debug, for now. clean later

    try:
        #print(temp_l,url[1],':',durl2m(url[1]))
        m,chan,c=await durl2m(url) #fails on threads because of "chan". but maybe just take the message id and extract channel information from that?
        print("afterdurl")
        txt=m.content
        print(m.channel)
        print(m.channel.name)
        try:
            strig="<@"+str(m.author.id)+"> in <#"+chan+">:\n"+txt
        except:
            strig="<@"+str(m.author.id)+"> in "+m.channel.name+":\n"+txt
        #print(strig)
        #await message.channel.send(strig) needs split as message could be long (2k chars. maybe better solution is simply to send two messages? tried it and it does not work. strange)
        await splitsend(channel,strig,False)
    except:
        await channel.send("some bug. are you sure that is a link to a discord message?")

        return

    await interaction.response.send_message("hope you got the output you wanted",ephemeral=True)


@tree.command()
@app_commands.describe(echome='text to echo')
async def slashatest(interaction: discord.Interaction, echome: str):
    await interaction.response.send_message(f'{echome=}', ephemeral=True)


@client.event #needed since it takes time to connect to discord
async def on_ready(): 
    tree.copy_global_to(guild=client.guilds[0])
    await tree.sync()
    print("slashayak is up!")
    print(tree.get_commands())
    return

async def durl2m(u): #needs to be redone for thread...
    print(u)
    url=u.split("/")
    url=list(reversed(url))
    print(url)
    c=client.guilds[0].get_channel_or_thread(int(url[1]))
    m=await c.fetch_message(int(url[0]))
    return m,url[1],c

async def splitsend(ch,st,codeformat):
#send data in chunks smaller than 2k
#might it have a bug of dropping last space and last line?
    if len(st)<1900: #discord limit is 2k and we want some play)
        if codeformat:
            await ch.send('```'+st+'```')
        else:
            await ch.send(st)
    else:
        x=st.rfind('\n',0,1900)
        if codeformat:
            await ch.send('```'+st[0:x]+'```')
        else:
            await ch.send(st[0:x])
        await splitsend(ch,st[x+1:],codeformat)

discord_token=os.getenv('SLASHAYAK_DISCORD_KEY')
client.run(discord_token) 
