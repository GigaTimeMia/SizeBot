import logging
import random

from discord.ext import commands, tasks
from sizebot.discordplus import commandsplus

from sizebot.lib import changes, proportions, userdb
from sizebot.lib.units import Rate

logger = logging.getLogger("sizebot")


class ChangeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        changes.loadFromFile()
        self.changeTask.start()

    def cog_unload(self):
        self.changeTask.cancel()

    @commandsplus.command(
        usage = "<x,-,/,+> <amount>"
    )
    @commands.guild_only()
    async def change(self, ctx, style, *, amount):
        """Change height."""
        guildid = ctx.guild.id
        userid = ctx.author.id

        proportions.changeUser(guildid, userid, style, amount)  # TODO: Switch to the method we use in Rates to parse this
        await proportions.nickUpdate(ctx.author)                # instead of forcing users to use two arguments.
        userdata = userdb.load(guildid, userid)

        logger.info(f"User {userid} ({ctx.author.display_name}) changed {style}-style {amount}.")
        await ctx.send(f"User <@{userid}> is now {userdata.height:m} ({userdata.height:u}) tall.")

    @commandsplus.command(
        hidden = True
    )
    @commands.is_owner()
    async def changes(self, ctx):
        await ctx.message.delete(delay=0)

        changeDump = changes.formatSummary()

        if not changeDump:
            changeDump = "No active changes"

        await ctx.author.send("**ACTIVE CHANGES**\n" + changeDump)
        logger.info(f"User {ctx.author.id} ({ctx.author.display_name}) dumped the running changes.")

    @commandsplus.command(
        usage = "<rate>"
    )
    @commands.guild_only()
    async def slowchange(self, ctx, *, rateStr: str):
        """Change your height steadily over time.

        Set how fast or slow you'd like to change, and when you'd like to stop.
        Examples:
        `&slowchange 1m/s`
        `&slowchange 1m/s until 10m`
        `&slowchange 1m/s for 1h`"""
        userid = ctx.author.id
        guildid = ctx.guild.id

        addPerSec, mulPerSec, stopSV, stopTV = Rate.parse(rateStr)

        changes.start(userid, guildid, addPerSec=addPerSec, mulPerSec=mulPerSec, stopSV=stopSV, stopTV=stopTV)

        await ctx.send(f"{ctx.author.display_name} has begun slow-changing at a rate of `{rateStr}`.")
        logger.info(f"User {ctx.author.id} ({ctx.author.display_name}) slow-changed {addPerSec}/sec and *{mulPerSec}/sec until {stopSV} for {stopTV} seconds.")

    @commandsplus.command()
    @commands.guild_only()
    async def stopchange(self, ctx):
        """Stop a currently active slow change."""
        userid = ctx.author.id
        guildid = ctx.guild.id

        deleted = changes.stop(userid, guildid)

        if deleted is None:
            await ctx.send("You can't stop slow-changing, as you don't have a task active!")
            logger.warn(f"User {ctx.author.id} ({ctx.author.display_name}) tried to stop slow-changing, but there didn't have a task active.")
        else:
            await ctx.send(f"{ctx.author.display_name} has stopped slow-changing.")
            logger.info(f"User {ctx.author.id} ({ctx.author.display_name}) stopped slow-changing.")

    @commandsplus.command()
    @commands.guild_only()
    async def eatme(self, ctx):
        """Eat me!

        Increases your height by a random amount between 2x and 20x."""
        guildid = ctx.guild.id
        userid = ctx.author.id

        userdata = userdb.load(guildid, userid)
        randmult = round(random.randint(2, 20), 1)
        proportions.changeUser(guildid, userid, "multiply", randmult)
        await proportions.nickUpdate(ctx.author)

        # TODO: Randomize the italics message here
        await ctx.send(
            f"<@{userid}> ate a :cake:! *I mean it said \"Eat me...\"*\n"
            f"They multiplied {randmult}x and are now {userdata.height:m} tall. ({userdata.height:u})")
        logger.info(f"User {userid} ({ctx.author.display_name}) ate a cake and multiplied {randmult}.")

    @commandsplus.command()
    @commands.guild_only()
    async def drinkme(self, ctx):
        """Drink me!

        Decreases your height by a random amount between 2x and 20x."""
        guildid = ctx.guild.id
        userid = ctx.author.id

        userdata = userdb.load(guildid, userid)
        randmult = round(random.randint(2, 20), 1)
        proportions.changeUser(guildid, ctx.author.id, "divide", randmult)
        await proportions.nickUpdate(ctx.author)

        # TODO: Randomize the italics message here
        await ctx.send(
            f"<@{ctx.author.id}> ate a :milk:! *I mean it said \"Drink me...\"*\n"
            f"They shrunk {randmult}x and are now {userdata.height:m} tall. ({userdata.height:u})")
        logger.info(f"User {ctx.author.id} ({ctx.author.display_name}) drank a potion and shrunk {randmult}.")

    @tasks.loop(seconds=6)
    async def changeTask(self):
        """Slow growth task"""
        await changes.apply(self.bot)


def setup(bot):
    bot.add_cog(ChangeCog(bot))
