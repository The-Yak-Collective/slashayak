## parts from here: https://gist.github.com/Rapptz/c4324f17a80c94776832430007ad40e6#slash-commands-and-context-menu-commands

    


from discord.app_commands import Choice
from discord.ext import tasks, commands
import discord
import asyncio
import os
import re
import subprocess
import time
import datetime
from dotenv import load_dotenv

import sqlite3
import logging


from discord_slashayak import * #including client and tree

HOME_DIR="/home/yak/robot/slashayak/"
USER_DIR="/home/yak/"

load_dotenv(USER_DIR+'.env')

conn=sqlite3.connect(HOME_DIR+'slashayakdatabase.db') #the connection should be global. 


db_c = conn.cursor()

@tasks.loop(minutes=60*11)
async def pulseall():
    pulseus=db_c.execute('select threadid from pulses').fetchall()
    print('will now pulse ',pulseus)
    for i in pulseus:
        pulse(chan(i[0]))

@tree.command(description= "unfurl single messages in and from threads as well as regular channels") # at this time only single link only, sorry. later to add a whole thread, i guess
@app_commands.describe(linktounfurl='the link to unfurl')
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

@tree.command(description="(soon obsolete) set a prompt for ongoing discussions")
@app_commands.describe(theprompt='text of prompt')
async def promptset(interaction: discord.Interaction, theprompt: str):
    conts=theprompt
    db_c.execute('''insert into prompts values (NULL,?,?,?,?,?,?,?)''',(str(interaction.user.id),conts,0,int(time.time()),0,interaction.channel_id,"not in use"))
    conn.commit()
    await interaction.response.send_message("hope you like your prompt! \nuse /promptset again to change it, /promptshow to show it to all and /promptrecall to show it only to yourself", ephemeral=True)
    return

@tree.command( description="(soon obsolete) private reminder of the current prompt of this for ongoing discussions")
async def promptrecall(interaction: discord.Interaction):
    try:
        rows=db_c.execute('select contents from prompts where chan=? order by  promptid desc',(interaction.channel_id,)).fetchone()
    except:
        rows=["could not obtain prompt"]
    if not rows:
        rows=["are you sure you created a prompt?"]
    await interaction.response.send_message("the prompt:\n"+rows[0], ephemeral=True)
    return

@tree.command( description="(soon obsolete) show the current prompt of this for ongoing discussions")
async def promptshow(interaction: discord.Interaction):
    try:
        rows=db_c.execute('select contents from prompts where chan=? order by promptid desc',(interaction.channel_id,)).fetchone()
    except:
        rows=["could not obtain prompt"]
    if not rows:
        rows=["are you sure you created a prompt?"]
    await splitsend(interaction.channel,rows[0],False)
    await interaction.response.send_message("done", ephemeral=True)
    return


@tree.command(description="a simple echo as a test")
@app_commands.describe(echome='text to echo')
async def slashatest(interaction: discord.Interaction, echome: str):
    await interaction.response.send_message(f'{echome=}', ephemeral=True)

@tree.command(description="pulse a thread - will it come back to life? (yes!)")
@app_commands.describe(threadid='ID of thread we want to pulse')
async def slashapulse(interaction: discord.Interaction, threadid: str):
    th=await chan(i)
    await pulse(th)
    return

async def chan(i):
    th=client.guilds[0].get_channel_or_thread(int(threadid))
    if th==None:
        th=client.guilds[0].get_thread(int(threadid))
        if th==None:
            th=await client.guilds[0].fetch_channel(int(threadid))
    return th
    
@tree.command(description="pulse a thread every 11 hours")
@app_commands.describe(onoff='to pulse current thread or not')
@app_commands.choices(onoff=[
    Choice(name='on', value=1),
    Choice(name='off', value=0),])

async def pulseaday(interaction: discord.Interaction, onoff: Choice[int]): #actually every 11 hours
    thid=interaction.channel_id
    print ('pulse a day',thid,reaction.value)
    if(reaction.value==1):
        await pulse(interaction.channel)
        db_c.execute('''insert into pulses values (NULL,?)''',(thid,))
    if(reaction.value==0):
        db_c.execute('''delete from pulses where threadid=? ''',(thid,))
    conn.commit()

    return

async def pulse(th):
    await th.send('staying alive', delete_after=10)


@client.event #needed since it takes time to connect to discord
async def on_ready(): 
    tree.copy_global_to(guild=client.guilds[0])
    m= await tree.sync(guild=client.guilds[0])
    tree.clear_commands(guild=None)
    m= await tree.sync()
    print([x.name for x in m])
    checkon_database()
    print("slashayak is up!")
    print([x.name for x in tree.get_commands()])
    pulseall.start()
    return

async def durl2m(u): #needs to be redone for thread...
    print(u)
    url=u.split("/")
    url=list(reversed(url))
    print(url)
    c=client.guilds[0].get_channel_or_thread(int(url[1]))
    m=await c.fetch_message(int(url[0]))
    return m,url[1],c

def checkon_database(): 
#check if table exists in DB. if not, create it
#this function is RIPE for automation, which would also be carried over to "on message"
    db_c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='prompts' ''')
    if db_c.fetchone()[0]!=1:
        db_c.execute('''CREATE TABLE prompts (promptid INTEGER PRIMARY KEY, creatorid text, contents text, filled int, createdat int, filledat int, chan int, mlink text)''') 
        #filled=is it active
        #most items will not be used...
        conn.commit()
    db_c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pulses' ''')
    if db_c.fetchone()[0]!=1:
        db_c.execute('''CREATE TABLE pulses (entry INTEGER PRIMARY KEY, threadid INTEGER)''') 
        conn.commit()


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
