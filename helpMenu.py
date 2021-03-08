import discord


def getHelpPages():
    totalPages = 6

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



    page4 = discord.Embed(
        title = "Minecraft",
        description = f"Page 4/{totalPages}",
        color = discord.Color.gold()
    )
    page4.add_field(
        name="^mc <server IP>",
        value = "Displays information about the given server IP. If ommited, our server's [pogland.ggs.onl] will be shown instead.",
        inline = False
    )
    page4.add_field(
        name="^status",
        value="Displays Mojang's server status."
    )




    page5 = discord.Embed(
        title = "Games",
        description = f"Page 5/{totalPages}",
        color = discord.Color.gold()
    )
    page5.add_field(
        name="^rps [member]",
        value="Initiates a rock, paper, scissors game with the given member.",
        inline=False
    )
    page5.add_field(
        name="^ss",
        value="""
            ^ss setup: sets up required roles and channel for a Simon Says game. Ideally should only be used once.
            ^ss start: starts a Simon Says game.
            ^ss disqualify: disqualify a member from the ongoing Simon Says game.
        """
    )

    page6 = discord.Embed(
        title = "Miscellaneous",
        description = f"6/{totalPages}",
        color = discord.Color.gold()
    )

    page6.add_field(
        name="^afk <reason>",
        value = "Sets your status as AFK with the given reason.",
        inline = False
    )
    
    
    return [page1, page2, page3, page4, page5, page6]