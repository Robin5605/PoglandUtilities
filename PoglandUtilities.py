import discord
from discord import Intents, MemberCacheFlags
from discord.ext import commands
from helper import *
import asyncio

# INTENTS
# Intents.members
# Intents.guilds

intents = Intents(members=True, guilds=True, messages=True)
client = commands.Bot(command_prefix="!u ", intents=intents)

TOKEN = "REDACTED"

@client.event
async def on_ready():
    print("Connected!")

@client.command()
@commands.has_permissions(administrator=True)
async def membercount(ctx):
    guild = ctx.guild
    if not checkMemberCountExists(client): #if a valid member count channel doesn't exist, then set it up.
        members = guild.member_count

        perms = {
            guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True),
            guild.me: discord.PermissionOverwrite(manage_channels=True)
        }

        channel = await guild.create_voice_channel(f"Members: {members}", overwrites=perms, position=0)
        add("memberCount", channel.id)
    else: #if it does, then send a message saying it is already set up.
        await embedBuilder(ctx, "Member count has already been set up.")

@client.command()
@commands.has_permissions(administrator=True)
async def lock(ctx, time=None):
    channel = ctx.channel
    guild = ctx.guild
    lockDict = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False)
    }

    await channel.edit(overwrites=lockDict)
    if time is not None:
        try:
            if time[-1] == "s" or time[-1] == "m" or time[-1] == "h":
                await logger(ctx, client, "lock", time) #log the channel lock
                
                await asyncio.sleep(int(time[0:-1])) #wait specified amount of time
                await ctx.invoke(unlock) #trigger unlock function
            else:
                await embedBuilder(ctx, "Valid time not entered. Channel muted until `!u unlock` command is issued.", discord.Color.red())
                await logger(ctx, client, "lock", time) #log the channel lock
        except:
            await embedBuilder(ctx, "Valid time not entered. Channel muted until `!u unlock` command is issued.", discord.Color.red())
            await logger(ctx, client, "lock", time) #log the channel lock
    else:
        await logger(ctx, client, "lock")
        
@client.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    channel = ctx.channel
    guild = ctx.guild
    unlock = {
        guild.default_role: discord.PermissionOverwrite(send_messages=True)
    }

    await logger(ctx, client, "unlock")

    await channel.edit(overwrites=unlock)

@client.command()
@commands.has_permissions(administrator=True)
async def log(ctx):
    channel = ctx.message.channel_mentions
    if len(channel) > 0:
        add("log", channel[0].id)
        await embedBuilder(ctx, f"Log channel successfully set to {channel[0].mention}")
    else:
        if checkLogChannelExists(client)
            await embedBuilder(ctx, f"Your log channel is currently {client.get_channel(get('log')).mention}")
        else:
            await embedBuilder(ctx, f"You don't have a log channel right now. Set one using `!u log #channel`")

@client.command()
async def echo(ctx, arg1):
    await ctx.send(arg1)

@client.event
async def on_member_join(member):
    if checkMemberCountExists(client):
        members = member.guild.member_count
        channel = client.get_channel(get("memberCount"))

        await channel.edit(name=f"Members:{members}")
@client.event
async def on_member_remove(member): 
    if checkMemberCountExists(client):
        members = member.guild.member_count
        channel = client.get_channel(get("memberCount"))

        await channel.edit(name=f"Members:{members}")

@client.event
async def on_message(message):
    countingChannel = client.get_channel(get("countingChannel"))
    if not message.author == client.user and message.channel == countingChannel: #if message is not sent by bot and is in the counting channel
        try:
            number = int(message.content) #if the message is not an integer it will throw an error
            if number == get("counting") + 1:
                add("counting", int(message.content)) #updates the number in info.json
            else:
                await message.delete()
                await countingLogger(client, message) #log the incorrect number

        except:
            await message.delete() #if message is not an integer it will be deleted
            await countingLogger(client, message) #log the incorrect number
    await client.process_commands(message)

@client.command()
@commands.has_permissions(administrator=True)
async def override(ctx, number: int):
    countingChannel = client.get_channel(get("countingChannel"))
    if not ctx.channel == countingChannel: #prevents execution of commands in counting channel
        add("counting", number)
        await embedBuilder(ctx, f"Counting will now start from **{number}**.")

@client.event
async def on_guild_join(guild):
    #setting these values to 0 invalidates them
    add("memberCount", 0)
    add("logChannel", 0)
    add("countingChannel", 0)
    add("counting", 0)

@client.command()
@commands.has_permissions(administrator=True)
async def countingChannel(ctx):
    channel = ctx.message.channel_mentions
    if len(channel) > 0:
        add("countingChannel", channel[0].id)
        await embedBuilder(ctx, f"Log channel successfully set to {channel[0].mention}")
    else:
        if checkCountingChannelExists(client):
            await embedBuilder(ctx, f"Your counting channel is currently {client.get_channel(get('countingChannel')).mention}")
        else:
            await embedBuilder(ctx, f"You don't have a counting channel right now. Set one using `!u countingChannel #channel`") 

@client.event
async def on_command_error(ctx, error):
    if(isinstance(error, commands.errors.MissingPermissions)):
        await embedBuilder(ctx, "You must be an administrator to run that command.", discord.Color.red())
    else:
        await ctx.send(error)
client.run(TOKEN)
