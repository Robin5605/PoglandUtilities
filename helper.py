import json
import discord

def getToken():
    with open("token.txt", "r") as f:
        return f.read()

def add(key, value):
    with open("info.json", "r") as f:
        info = json.load(f)
    info[key] = value
    with open("info.json", "w") as f:
        json.dump(info, f, indent=4)

def delete(key):
    with open("info.json", "r") as f:
        info = json.load(f)
    del info[key]
    with open("info.json", "w") as f:
        json.dump(info, f, indent=4)
def get(key=None):
    if key is None:
        with open("info.json", "r") as f:
            info = json.load(f)
        return info
    else:
        with open("info.json", "r") as f:
            info = json.load(f)
        return info[key]

def checkMemberCountExists(client):
    if "memberCount" in get(): #check if "memberCount" key exists
        channel = client.get_channel(get("memberCount"))
        if channel is None: #if key exists but channel is not valid (i.e deleted member count) then return false
            return False
        else: #key exists and channel is a valid, currently-existing channel
            return True
    else: #false if the key doesn't exist at all (i.e not been set up yet.)
        return False
def checkLogChannelExists(client):
    if "log" in get(): #check if "log" key exists
        channel = client.get_channel(get("log"))
        if channel is None: #if key exists but channel is not valid (i.e deleted log channel) then return false
            return False
        else: #key exists and channel is a valid, currently-existing channel
            return True
    else: #false if the key doesn't exist at all (i.e not been set up yet.)
        return False

def checkCountingChannelExists(client):
    if "countingChannel" in get(): #check if "log" key exists
        channel = client.get_channel(get("countingChannel"))
        if channel is None: #if key exists but channel is not valid (i.e log channel disabled then return false
            return False
        else: #key exists and channel is a valid, currently-existing channel
            return True
    else: #false if the key doesn't exist at all (i.e not been set up yet.)
        return False

async def embedBuilder(ctx, text, color=discord.Color.green()):
    embed = discord.Embed(
        title = "",
        description = text,
        color = color
    )
    await ctx.send(embed=embed)


async def logger(ctx, client, command, duration=None):
    if checkLogChannelExists:
        if command == "lock":

            logChannel = client.get_channel(get("log"))
            unit = ""
            time = ""

            if duration is None:
                time = "Until `^unlock` is issued."
                await embedBuilder(ctx, "Channel locked until `^unlock` is issued :lock:")
            else:
                time = duration[0:-1]
                if duration[-1] == "s":
                    unit = "seconds"
                elif duration[-1] == "m":
                    unit = "minutes"
                elif duration[-1] == "h":
                    unit = "hours"
                await embedBuilder(ctx, f"Channel locked for {time} {unit} :lock:")

            log = discord.Embed(
                title = "Pogland Utilities Log",
                description = "Channel locked :lock:",
                color = discord.Color.blue()
            )
            log.add_field(
                name = "Channel",
                value = f"{ctx.channel.mention}",
                inline = True
            )
            log.add_field(
                name = "Duration",
                value = f"{time} {unit}",
                inline = True
            )
            log.add_field(
                name = "User",
                value = f"{ctx.author.mention}",
                inline = False
            )

            
            await logChannel.send(embed=log)
        elif command == "unlock":
            logChannel = client.get_channel(get("log"))
            log = discord.Embed(
                title = "Pogland Utilities Log",
                description = "Channel unlocked :unlock:",
                color = discord.Color.blue()
            )
            log.add_field(
                name = "Channel",
                value = f"{ctx.channel.mention}",
                inline = True
            )
            log.add_field(
                name = "User",
                value = f"{ctx.author.mention}",
                inline = True
            )

            await embedBuilder(ctx, f"Channel unlocked :unlock:")
            await logChannel.send(embed=log)
async def countingLogger(client, message):
    expected = get("counting") + 1
    log = discord.Embed(
        title = "Counting Log",
        description = f"{message.author.mention} entered \"{message.content}\" instead of {expected}.",
        color = discord.Color.blue()
    )
    await client.get_channel(get("log")).send(embed=log)