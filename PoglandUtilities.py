import discord
from discord import Intents, MemberCacheFlags
from discord.ext import commands
from helper import *
import asyncio
from typing import Union
import helpMenu
import requests

# INTENTS
# Intents.members
# Intents.guilds

client = commands.Bot(command_prefix="!", intents=Intents.all())
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

    if message.author in client.afk:
        try:
            await message.author.edit(nick=f"{message.author.nick[6:] if message.author.nick else message.author.name}") #removes the [AFK] prefix
        except:
            pass
        del client.afk[message.author]
        await message.channel.send(f"Welcome back, {message.author.mention}! I've removed your AFK status.")

    for afkMember in client.afk:
        for mention in message.mentions:
            if mention == afkMember:
                embed = discord.Embed(
                    title = "",
                    description = f"""
                        {mention.mention} is AFK
                        They left the note: {client.afk[afkMember]["reason"]}
                        [This]({client.afk[afkMember]["message"].jump_url}) was their last message.
                    """,
                    color = discord.Color.green()
                )
                await message.channel.send(embed=embed)

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
async def role(ctx, member : discord.user, role : discord.Role):
    await member.add_roles(role)
    await embedBuilder(ctx, f"{member.mention} now has the \"{role.name}\" role.")

@client.command()
async def help(ctx):
    currentPage = 0
    totalPages = 6
    menuOpen = True #whether or not the user has reacted with ⏹️

    helpMenuMessage = await ctx.send(embed=helpMenu.getHelpPages()[currentPage]) #the initial help menu page
    

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
            if currentPage == 0: #if the current page is 1 and the user has requested to see the previous page, set the current page to the last page
                currentPage = totalPages - 1

            elif currentPage < totalPages: #If the current page is less than  the total pages, then decrement the current page value
                currentPage -= 1

            await reaction.remove(user)
            await helpMenuMessage.edit(embed=helpMenu.getHelpPages()[currentPage])
        elif reaction.emoji == "▶️":
            if currentPage == totalPages - 1: #if the current page is the last page and the user has requested to see the next page, set the current page to the first page
                currentPage = 1

            elif currentPage >= 0: #If the current page is greater or equal to 0, then increment the current page value
                currentPage += 1

            await reaction.remove(user)
            await helpMenuMessage.edit(embed=helpMenu.getHelpPages()[currentPage])


@client.command()
async def mc(ctx, ip="pogland.ggs.onl"):
    request = requests.get(f'https://api.mcsrvstat.us/2/{ip}')
    srvinfo = request.json() #main dictionary with all server information
    client.playerDisplay = ""


    if srvinfo["ip"] == "": #if server doesn't exist
        await embedBuilder(ctx, "That server doesn't exist.", discord.Color.red())
    else:
        embed = discord.Embed(
            title = "Minecraft server info",
            description = f"Hostname: {srvinfo['hostname']}",
            color = discord.Color.green()
        )
        if srvinfo["debug"]["ping"] == True: #if pinging is allowed on this server
            embed.add_field(
                name = "Server",
                value = f"""
                        Status: {"online" if srvinfo["online"] else "offline"}
                        Version: {srvinfo["version"]}
                        IP: {srvinfo["ip"]}:{srvinfo["port"]}
                """,
                inline = False
            )

            if "icon" in srvinfo: #if icon exists
                iconURL = f"https://api.mcsrvstat.us/icon/{ip}"
                embed.set_thumbnail(url=iconURL)

            if "players" in srvinfo:
                
                if "list" in srvinfo["players"]:
                    afkList = getAFK() #gets a list of afk players
                    for player in srvinfo['players']['list']:
                        if player in afkList:
                            client.playerDisplay += f"[{player}](https://mine.ly/{player}/) [AFK]\n"
                        else:
                            client.playerDisplay += f"[{player}](https://mine.ly/{player}/)\n"
                    embed.add_field(
                        name = f"Players: {srvinfo['players']['online']}/{srvinfo['players']['max']}",
                        value = client.playerDisplay,
                        inline = False
                    )
                else:
                    embed.add_field(
                        name = f"Players: {srvinfo['players']['online']}/{srvinfo['players']['max']}",
                        value = "Either there are no players online or this server doesn't allow checking online players",
                        inline = False
                    )
            else:
                embed.add_field(
                    name = "Unable to show players",
                    value = "This server doesn't allow checking online players.",
                    inline = False
                )
        else:
            embed.add_field(
                name = "Server",
                value = f"""
                        Status: {"online" if srvinfo["online"] else "offline"}
                        Version: Unable to show
                        IP: {srvinfo["ip"]}:{srvinfo["port"]}
                """,
                inline = False
            )

            embed.add_field(
                name = "Unable to show players",
                value = "Pinging is disabled for this server.",
                inline = False
            )
            

        await ctx.send(embed=embed)

@client.command()
async def status(ctx):
    r = requests.get("https://status.mojang.com/check")
    json = r.json()
    
    embed = discord.Embed(
        title = "Mojang Server Status",
        description = "",
        color = discord.Color.blue()
    )

    for i in json:
        url = list(i.keys())[0]

        if i[url] == "green": status = "🟩"
        elif i[url] == "yellow": status = "🟨"
        elif i[url] == "red": status = "🟥"

        embed.add_field(
            name = url,
            value = "Status: " + status,
            inline = False
        )
    
    

    await ctx.send(embed=embed)

@client.event
async def on_voice_state_update(member, before, after):
    guild = member.guild

    if before.channel is None and after.channel is not None: #on member join voice channel
        channel = after.channel #the voice channel the user joined
        

        if len(channel.members) == 1:
            channelRole = await guild.create_role(name=channel.name, color=discord.Color.green())
            await member.add_roles(channelRole)
        else:
            channelRole = discord.utils.get(guild.roles, name=channel.name)
            await member.add_roles(channelRole)

    elif before.channel is not None and after.channel is None: #on member leave voice channel
        channel = before.channel #the voice channel the user left

        if len(channel.members) == 0:
            channelRole = discord.utils.get(guild.roles, name=channel.name)
            await channelRole.delete()
        else:
            channelRole = discord.utils.get(guild.roles, name=channel.name)
            await member.remove_roles(channelRole)

inGame = [] #list of everyone in a game
@client.command()
async def rps(ctx, member : discord.Member):
    challenger = ctx.message.author
    if member == challenger:
        await embedBuilder(ctx, "You can't challenge yourself!", discord.Color.red())
    elif (member in inGame) or (challenger in inGame):
        await embedBuilder(ctx, "That person is already in a game. Please wait until they are done.", discord.Color.red())
    else:
        await embedBuilder(ctx, f"Challenging {member.mention} to a rock paper scissors match...")

        await challenger.send("Waiting for opponent to accept...")
        r = await member.send(f"{challenger.mention} would like to challenge you to a game of rock paper scissors. Accept?")
        
        await r.add_reaction('☑️')
        await r.add_reaction('❌')

        def check(reaction, user):
            return not user.bot

        reaction, user = await client.wait_for("reaction_add", check=check)

        if str(reaction.emoji) == '☑️': #if opponent accepts
            await challenger.send("Opponent has accepted!")

            inGame.append(challenger)
            inGame.append(member)

            options = {
                "r": "rock",
                "p": "paper",
                "s": "scissors"
            }

            await challenger.send("Type in r, p, or s: ")
            await member.send("Waiting for opponent to choose...")

            def check1(message): #for challenger
                return (message.content in options) and (message.author == challenger) and (isinstance(message.channel, discord.DMChannel))
            
            def check2(message): #for the person that was challenged
                return (message.content in options) and (message.author == member) and (isinstance(message.channel, discord.DMChannel))

            challengerReply = await client.wait_for("message", check=check1)
            await challenger.send("OK, now wait for opponent to choose.")
            await member.send("Your turn! Choose from r, p, or s.")

            memberReply = await client.wait_for("message", check=check2)
            
            if challengerReply.content == "r" and memberReply.content == "p":
                winner = member
            elif challengerReply.content == "p" and memberReply.content == "r":
                winner = challenger
            elif challengerReply.content == "p" and memberReply.content == "s":
                winner = member
            elif challengerReply.content == "s" and memberReply.content == "p":
                winner = challenger
            elif challengerReply.content == "r" and memberReply.content == "s":
                winner = challenger
            elif challengerReply.content == "s" and memberReply.content == "r":
                winner = member
            elif challengerReply.content == memberReply.content:
                winner = None
            else:
                print(challengerReply.content + ", "  + memberReply.content)

            if winner == member:
                await member.send(f"You won! Opponent chose __{options[challengerReply.content]}__ and you chose __{options[memberReply.content]}__")
                await challenger.send(f"You lost... Opponent chose __{options[memberReply.content]}__ and you chose __{options[challengerReply.content]}__")
            elif winner == challenger:
                await challenger.send(f"You won! Opponent chose __{options[memberReply.content]}__ and you chose __{options[challengerReply.content]}__")
                await member.send(f"You lost... Opponent chose __{options[challengerReply.content]}__ and you chose __{options[memberReply.content]}__")
            elif winner is None:
                await challenger.send(f"Draw! Both you and your opponent chose {options[challengerReply.content]}")
                await member.send(f"Draw! Both you and your opponent chose {options[challengerReply.content]}")

            inGame.remove(challenger)
            inGame.remove(member)

        elif str(reaction.emoji) == '❌':
            await challenger.send("Opponent has declined the challenge...")

@client.group()
async def ss(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("No subcommand...")

@ss.command()
async def setup(ctx):
    rolesMessage = await ctx.send("Setting up roles...")
    guild = ctx.guild

    def rolesExist():
        return discord.utils.get(guild.roles, name="Simon") and discord.utils.get(guild.roles, name="Competitor") and discord.utils.get(guild.roles, name="Disqualified")

    if not rolesExist():

        simon = await guild.create_role(name="Simon")
        competitor = await guild.create_role(name="Competitor")
        disqualified = await guild.create_role(name="Disqualified")

        await rolesMessage.edit(content=f"Created 3 new roles: {simon.mention}, {competitor.mention}, and {disqualified.mention}")
    else:
        await rolesMessage.edit(content="Roles already exist. Nothing changed.")

    channelMessage = await ctx.send("Setting up channel...")

    if discord.utils.get(guild.channels, name="simon-says") is None:
        global simonSaysChannel

        permissions = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True,send_messages=False),
            discord.utils.get(ctx.guild.roles, name="Simon"): discord.PermissionOverwrite(read_messages=True,send_messages=True),
            discord.utils.get(ctx.guild.roles, name="Competitor"): discord.PermissionOverwrite(read_messages=True,send_messages=True),
            discord.utils.get(ctx.guild.roles, name="Disqualified"): discord.PermissionOverwrite(read_messages=True,send_messages=False)
        }
        simonSaysChannel = await guild.create_text_channel("simon-says", overwrites=permissions)

        await channelMessage.edit(content=f"Created new channel {simonSaysChannel.mention} with correct permissions.")
    else:
        await channelMessage.edit(content="Channel already exists. Nothing changed.")
@ss.command()
async def start(ctx):
    guild = ctx.guild

    uncached = await ctx.send("A new Simon Says game is starting in 5 seconds. React with ✋ to enter.")
    await uncached.add_reaction('✋')
    message = await ctx.channel.fetch_message(uncached.id)
    

    await asyncio.sleep(5) #sleep 2 minutes
    reaction = message.reactions[0]

    for participant in await reaction.users().flatten():
        await participant.add_roles(discord.utils.get(ctx.guild.roles, name="Competitor"))

@ss.command()
async def disqualify(ctx, member : discord.Member):
    await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Competitor"))
    await member.add_roles(discord.utils.get(ctx.guild.roles, name="Disqualified"))

    await ctx.send(f"Disqualified {member.mention}.")

client.afk = {} #list of AFK members to reason
@client.command()
async def afk(ctx, *, reason="No reason provided."):
    member = ctx.message.author
    
    if member not in client.afk: 
        client.afk[member] = {}
        client.afk[member]["reason"] = reason
        client.afk[member]["message"] = ctx.message
        
        try:
            await member.edit(nick=f"[AFK] {member.nick if member.nick else member.name}")
            await ctx.send("Set your AFK status.")
        except discord.Forbidden:
            await ctx.send("I don't have permissions to change your nickname, but I still set you as AFK, though!")

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