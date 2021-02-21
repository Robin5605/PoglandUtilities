import discord
from discord import Intents, MemberCacheFlags
from discord.ext import commands
from helper import *
import asyncio
from typing import Union
import helpMenu


client = commands.Bot(command_prefix="^", intents=Intents.all())
client.remove_command("help") #remove the default help command

TOKEN = getToken()

@client.event
async def on_ready():
    print("Connected!")

originalPermissions = {}

@client.command()
@commands.has_permissions(administrator=True)
async def lock(ctx, time=None):
    channel = ctx.channel
    guild = ctx.guild

    global originalPermissions
    originalPermissions = channel.overwrites_for(guild.default_role)

    overwrite = channel.overwrites_for(guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(guild.default_role, overwrite=overwrite)
    
    if time is not None:
        try:
            if time[-1] == "s" or time[-1] == "m" or time[-1] == "h":
                await logger(ctx, client, "lock", time) #log the channel lock
                
                await asyncio.sleep(int(time[0:-1])) #wait specified amount of time
                await ctx.invoke(unlock) #trigger unlock function
            else:
                await embedBuilder(ctx, "Valid time not entered. Channel muted until `^unlock` command is issued.", discord.Color.red())
                await logger(ctx, client, "lock", time) #log the channel lock
        except:
            await embedBuilder(ctx, "Valid time not entered. Channel muted until `^unlock` command is issued.", discord.Color.red())
            await logger(ctx, client, "lock", time) #log the channel lock
    else:
        await logger(ctx, client, "lock")
        
@client.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    channel = ctx.channel
    guild = ctx.guild
    global originalPermissions

    await logger(ctx, client, "unlock")
    await channel.set_permissions(guild.default_role, overwrite=originalPermissions)

@client.command()
@commands.has_permissions(administrator=True)
async def log(ctx):
    channel = ctx.message.channel_mentions
    if len(channel) > 0:
        add("log", channel[0].id)
        await embedBuilder(ctx, f"Log channel successfully set to {channel[0].mention}")
    else:
        if checkLogChannelExists(client):
            await embedBuilder(ctx, f"Your log channel is currently {client.get_channel(get('log')).mention}")
        else:
            await embedBuilder(ctx, f"You don't have a log channel right now. Set one using `^log #channel`")

@client.command()
async def echo(ctx, arg1):
    await ctx.send(arg1)

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
            await embedBuilder(ctx, f"You don't have a counting channel right now. Set one using `^countingChannel #channel`") 

@client.command()
@commands.has_permissions(administrator=True)
async def role(ctx, memberInput: Union[discord.Member, int], roleInput: Union[discord.Role, str, int]):
    #The goal here is to parse every type of possible input to an object, whether it be role or user. If it's invalid, then we have to try to make it a NoneType

    if type(memberInput) is discord.Member: #if ping
        member = memberInput
    elif type(memberInput) is int: #if member id given
        member = ctx.guild.get_member(memberInput)

    if type(roleInput) is discord.Role: #if role ping
        role = roleInput
    elif type(roleInput) is str: #if role name given
        for role in ctx.guild.roles:
            if role.name == roleInput:
                role = role
                break
            else:
                role = None
    elif type(roleInput) is int: #if role id given
        role = ctx.guild.get_role(roleInput)

    
    if (type(role) is discord.Role) and (type(member) is discord.Member): #if role variable is a role object and member variable is a member object
        await member.add_roles(role)
        await embedBuilder(ctx, f"{member.mention} now has the {role.mention} role.")
    else:
        await embedBuilder(ctx, "Check given member and or role.", discord.Color.red())

@client.command()
async def help(ctx):
    currentPage = 1
    totalPages = helpMenu.getTotalPages()
    helpMenuMessage = await ctx.send(embed=helpMenu.getHelpPage(currentPage))
    menuOpen = True #whether or not the user has reacted with ⏹️

    controlEmojis = ["◀️", "⏹️", "▶️"]
    for emoji in controlEmojis:
        await helpMenuMessage.add_reaction(emoji)
    
    def check(reaction, user):
        #return true if the message that was reacted to was the help message, and the user who reacted was the user who requested the help menu, and the reacted emoji is in the controlEmojis list
        return reaction.message == helpMenuMessage and user == ctx.message.author and reaction.emoji in controlEmojis

    while menuOpen:
        reaction, user = await client.wait_for("reaction_add", check=check)
        if reaction.emoji == "⏹️":
            await helpMenuMessage.delete()
            menuOpen = False
        elif reaction.emoji == "◀️":
            if currentPage == 1: #if the current page is 1 and the user has requested to see the previous page, set the current page to the last page
                currentPage = totalPages
            elif currentPage <= totalPages: #If the current page is less or equal to the total pages, then decrement the current page value
                currentPage -= 1
            await reaction.remove(user)
            await helpMenuMessage.edit(embed=helpMenu.getHelpPage(currentPage))
        elif reaction.emoji == "▶️":
            if currentPage == totalPages: #if the current page is the total pages and the user has requested to see the next page, set the current page to the first page
                currentPage = 1
            elif currentPage >= 1: #If the current page is greater or equal to 1, then increment the current page value
                currentPage += 1

            await reaction.remove(user)
            await helpMenuMessage.edit(embed=helpMenu.getHelpPage(currentPage))

@client.event
async def on_command_error(ctx, error):
    if(isinstance(error, commands.errors.MissingPermissions)):
        await embedBuilder(ctx, "You must be an administrator to run that command.", discord.Color.red())
    elif isinstance(error, discord.ext.commands.BadUnionArgument):
        await embedBuilder(ctx, "Invalid syntax. Try again with the right syntax.", discord.Color.red())
    elif isinstance(error, discord.ext.commands.MissingPermissions):
        await embedBuilder(ctx, "Sorry, I don't have the permission to do that.", discord.Color.red())
    else:
        await ctx.send(error)
client.run(TOKEN)
