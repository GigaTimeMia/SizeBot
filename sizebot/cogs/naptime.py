import logging

from discord.ext import commands, tasks
from mongoengine import NotUniqueError

from sizebot.lib import naps
from sizebot.lib.units import TV

logger = logging.getLogger("sizebot")


class NaptimeCog(commands.Cog):
    """Commands for napping."""

    def __init__(self, bot):
        self.bot = bot
        self.nannyTask.start()

    def cog_unload(self):
        self.nannyTask.cancel()

    @commands.command(
        aliases = ["chloroform"],
        usage = "<duration>",
        category = "fun"
    )
    @commands.guild_only()
    async def naptime(self, ctx, *, delay: TV):
        """Go to bed in a set amount of time.

        Kicks you from any voice channel you're in after a set amount of time.
        """
        # TODO: Disable and hide this command on servers where bot does not have MOVE_MEMBERS permission
        if not ctx.me.guild_permissions.move_members:
            await ctx.send("Sorry, I don't have permission to kick users from voice channels")
            return

        logger.info(f"{ctx.author.display_name} wants to go to sleep in {delay:m}.")
        try:
            naps.schedule(ctx.author.id, ctx.guild.id, delay)
        except NotUniqueError:
            await ctx.send("You already have a nap scheduled.")
            return

        await ctx.send(f"See you in {delay:m}!")

    @commands.command(
        category = "fun"
    )
    @commands.guild_only()
    async def grump(self, ctx):
        """Too grumpy for bed time.

        Stops a &naptime command.
        """
        logger.info(f"{ctx.author.display_name} wants to cancel bedtime.")

        nanny = naps.cancel(ctx.author.id, ctx.guild.id)
        if nanny is not None:
            await ctx.send("Naptime has been cancelled.")

    @commands.command(
        aliases = ["nanny"],
        hidden = True,
        category = "mod"
    )
    @commands.is_owner()
    async def nannies(self, ctx):
        """Show me those nannies!
        """
        # PERMISSION: requires manage_messages
        await ctx.message.delete(delay=0)

        nannies = naps.get_nannies()

        if nannies.count() == 0:
            nanny_dump = "No active nannies."
        else:
            nanny_dump = "\n".join(str(n) for n in nannies)

        await ctx.author.send("**WAITING NANNIES**\n" + nanny_dump)
        logger.info(f"User {ctx.author.id} ({ctx.author.display_name}) dumped the waiting nannies.")

    @tasks.safe_loop(seconds=60)
    async def nannyTask(self):
        """Nanny task"""
        await naps.check(self.bot)


def setup(bot):
    bot.add_cog(NaptimeCog(bot))
