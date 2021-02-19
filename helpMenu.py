import discord

def getTotalPages():
    return 3

def getHelpPage(pageNumber):
    totalPages = getTotalPages()
    page1 = discord.Embed(
        title = "Channel locking & unlocking",
        description = f"Page 1/{totalPages}",
        color = discord.Color.gold()
    )
    page1.add_field(
        name = "^lock <Time>",
        value = "Locks the channel for the given amount of time. Time should be given as a number, followed by \"s\", \"m\", \"h\", for seconds, minutes, and hours respectively. If time is not given, then the channel will be locked until the `^unlock` command is issued",
        inline = False
    )
    page1.add_field(
        name = "^unlock",
        value = "Unlocks the channel. Usually for use when `^lock` is issued without parameters.",
        inline = False
    )

    page1.set_footer(text="Parameters in \"<>\" are optional parameters.")

    page2 = discord.Embed(
        title = "Settings",
        description = f"Page 2/{totalPages}",
        color = discord.Color.gold()
    )
    page2.add_field(
        name = "^log <#channel>",
        value = "Sets the log channel to the one mentioned. If omitted, the current log channel will be displayed instead.",
        inline = False
    )

    page2.add_field(
        name = "^override [number]",
        value = "Number to begin counting from. Useful if counting functionality is broken.",
        inline = False
    )

    page2.add_field(
        name = "^countingChannel <#channel>",
        value = "The channel for the counting functionality to watch. If ommited, current counting channel will be displayed.",
        inline = False
    )

    page3 = discord.Embed(
        title = "Moderation",
        description = f"Page 3/{totalPages}",
        color = discord.Color.gold()
    )
    page3.add_field(
        name = "^role [User (PING | ID)] [Role (PING | ID | NAME)]",
        value = "Gives the specified role to a user. Useful for large servers where scrolling and finding members is difficult. Note that the user parameter can be a ping or an id, while hte role can be a ping, an id, or a name. Role names with whitespaces much be in quotations.",
        inline = False
    )
    
    page2.set_footer(text="Parameters in \"<>\" are optional parameters.")
    
    #Driver
    if pageNumber == 1:
        return page1
    elif pageNumber == 2:
        return page2
    elif pageNumber == 3:
        return page3