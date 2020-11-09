import asyncio
import logging
from shutil import copyfile

from discord.utils import get
from discord.ext import commands

from sizebot import conf
from sizebot.lib import errors, proportions, userdb, paths
from sizebot.lib.constants import ids, emojis

logger = logging.getLogger("sizebot")


async def addUserRole(member):
    role = get(member.guild.roles, id=ids.sizebotuserrole)
    if role is None:
        logger.warn(f"Sizebot user role {ids.sizebotuserrole} not found in guild {member.guild.id}")
        return
    await member.add_roles(role, reason="Registered as sizebot user")


async def removeUserRole(member):
    role = get(member.guild.roles, id=ids.sizebotuserrole)
    if role is None:
        logger.warn(f"Sizebot user role {ids.sizebotuserrole} not found in guild {member.guild.id}")
        return
    await member.remove_roles(role, reason="Unregistered as sizebot user")


async def showNextStep(ctx, userdata):
    congrats = False
    if congrats:
        await ctx.send(f"Congratulations, {ctx.author.display_name}, you're all set up with SizeBot! Here are some next steps you might want to take:\n* You can use `{conf.prefix}setspecies` to set your species to be shown in your sizetag.\n* You can adjust your current height with `{conf.prefix}setheight`.\n* You can turn off sizetags with `{conf.prefix}setdisplay`.")
    if userdata.registered:
        return
    next_step = userdata.registration_steps_remaining[0]
    step_messages = {
        "setheight": f"To start, set your base height with `{conf.prefix}setbaseheight`. This should be roughly a human-sih size in order for comparisons to make better sense.",
        "setweight": f"Now, use `{conf.prefix}setbaseweight` to set your base weight. This should be whatever weight you'd be at your base height.",
        "setsystem": f"Finally, use `{conf.prefix}setsystem` to set what unit system you use: `M` for Metric, `U` for US."
    }
    next_step_message = step_messages[next_step]
    await ctx.send(f"You have {len(userdata.registration_steps_remaining)} registration steps remaining.\n{next_step_message}")


class RegisterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Change the way this works.
    @commands.command(
        aliases = ["signup"],
        category = "setup"
    )
    @commands.guild_only()
    async def register(self, ctx):
        # nick: str
        # currentheight: SV = proportions.defaultheight
        # baseheight: SV = proportions.defaultheight
        # baseweight: WV = userdb.defaultweight
        # unitsystem: str = "m"
        # species: str = None
        """Registers a user for SizeBot."""
        # Already registered

        userdata = None
        try:
            userdata = userdb.load(ctx.guild.id, ctx.author.id, allow_unreg=True)
        except errors.UserNotFoundException:
            userdata = None

        # User data already exists
        if userdata:
            if userdata.registered:
                await ctx.send("Sorry! You already registered with SizeBot.\n"
                               "To unregister, use the `&unregister` command.")
            else:
                await showNextStep(ctx, userdata)
            return

        # User is already in different guilds, offer to copy profile to this guild?
        guild_names = [self.bot.get_guild(int(g)).name for g, _ in userdb.listUsers(userid=ctx.author.id)]
        if guild_names:
            guildsstring = guild_names.join('\n')
            sentMsg = await ctx.send(f"You are already registered with SizeBot in these servers:\n{guildsstring}"
                                     f"You can copy a profile from one of these guilds to this one using `{ctx.prefix}copy.`\n"
                                     "Proceed with registration anyway?")
            await sentMsg.add_reaction(emojis.check)
            await sentMsg.add_reaction(emojis.cancel)

            # Wait for requesting user to react to sent message with emojis.check or emojis.cancel
            def check(reaction, reacter):
                return reaction.message.id == sentMsg.id \
                    and reacter.id == ctx.author.id \
                    and (
                        str(reaction.emoji) == emojis.check
                        or str(reaction.emoji) == emojis.cancel
                    )

            try:
                reaction, ctx.author = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                # User took too long to respond
                await sentMsg.delete()
                return

            # if the reaction isn't the right one, stop.
            if reaction.emoji != emojis.check:
                return

        userdata = userdb.User()
        userdata.guildid = ctx.guild.id
        userdata.id = ctx.author.id
        userdata.nickname = ctx.author.display_name
        if any(c in ctx.author.display_name for c in "()[]"):
            ctx.send("TODO: CLEANUP - If you have already have size tag in your name, you fix your nick with .setnick")
        userdata.display = "y"
        userdata.registration_steps_remaining = ["setheight", "setweight", "setsystem"]

        userdb.save(userdata)

        await addUserRole(ctx.author)

        logger.warn(f"Started registration for a new user: {ctx.author}!")
        logger.info(userdata)

        # user has display == "y" and is server owner
        if userdata.display and userdata.id == ctx.author.guild.owner.id:
            await ctx.send("I can't update a server owner's nick. You'll have to manage it manually.")

        await ctx.send("Initial registration completed! Registration can be finalized by running the following commands: INSERT COMMANDS HERE")
        await showNextStep(ctx, userdata)

    @register.error
    async def register_handler(self, ctx, error):
        # Check if required argument is missing
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Not enough variables for `register`.\n"
                "See `&help register`.".replace("&", self.bot.command_prefix))
            return
        raise error

    @commands.command(
        category = "setup"
    )
    @commands.guild_only()
    async def unregister(self, ctx):
        """Unregister your SizeBot profile."""
        guild = ctx.guild
        user = ctx.author
        # User is not registered
        if not userdb.exists(guild.id, user.id):
            logger.warn(f"User {user.id} not registered with SizeBot, but tried to unregister anyway.")
            await ctx.send("Sorry! You aren't registered with SizeBot.\n"
                           "To register, use the `&register` command.")
            return

        # Send a confirmation request
        # TODO: Replace this with a Menu.
        sentMsg = await ctx.send(f"To unregister, react with {emojis.check}.")
        await sentMsg.add_reaction(emojis.check)
        await sentMsg.add_reaction(emojis.cancel)

        # Wait for requesting user to react to sent message with emojis.check or emojis.cancel
        def check(reaction, reacter):
            return reaction.message.id == sentMsg.id \
                and reacter.id == user.id \
                and (
                    str(reaction.emoji) == emojis.check
                    or str(reaction.emoji) == emojis.cancel
                )

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            # User took too long to respond
            return
        finally:
            # User took too long OR User clicked the emoji
            await sentMsg.delete()

        # if the reaction isn't the right one, stop.
        if reaction.emoji != emojis.check:
            return

        # remove the sizetag, delete the user file, and remove the user role
        await proportions.nickReset(user)
        userdb.delete(guild.id, user.id)
        await removeUserRole(user)

        logger.warn(f"User {user.id} successfully unregistered.")
        await ctx.send(f"Unregistered {user.name}.")

    @commands.command(
        category = "setup"
    )
    @commands.guild_only()
    async def copy(self, ctx):
        """Copy your SizeBot profile from a different guild to this one."""

        inputdict = {
            "1️⃣": 1,
            "2️⃣": 2,
            "3️⃣": 3,
            "4️⃣": 4,
            "5️⃣": 5,
            "6️⃣": 6,
            "7️⃣": 7,
            "8️⃣": 8,
            "9️⃣": 9,
            "0️⃣": 10
        }

        guildsregisteredin = [g for g, _ in userdb.listUsers(userid = ctx.author.id)]
        guildsregisteredinnames = [self.bot.get_guild(g).name for g in guildsregisteredin]

        if guildsregisteredin == []:
            await ctx.send("You are not registered with SizeBot in any guilds."
                           f"To register, use `{ctx.prefix}register`.")
            return

        # TODO: This doesn't seem to work.
        if guildsregisteredin == [ctx.guild.id]:
            await ctx.send("You are not registered with SizeBot in any other guilds.")
            return

        outmsg = await ctx.send(emojis.loading)
        outstring = ""

        if userdb.exists(ctx.guild.id, ctx.author.id):
            outstring += "**:rotating_light:WARNING::rotating_light:**\n**You are already registered with SizeBot on this guild. Copying a profile to this guild will overwrite any size data you have here. Proceed with caution.**\n\n"

        outstring += "Copy profile from what guild?\n"

        # TODO: Replace this with a Menu.
        for i in range(min(len(guildsregisteredin), 10)):  # Loops over either the whole list of guilds, or if that's longer than 10, 10 times.
            outstring += f"{list(inputdict.keys())[i]} *{guildsregisteredinnames[i]}*\n"
            await outmsg.add_reaction(list(inputdict.keys())[i])
        await outmsg.add_reaction(emojis.cancel)

        outstring += f"\nClick {emojis.cancel} to cancel."

        await outmsg.edit(content = outstring)

        # Wait for requesting user to react to sent message with emojis.check or emojis.cancel
        def check(reaction, reacter):
            return reaction.message.id == outmsg.id \
                and reacter.id == ctx.author.id \
                and (
                    str(reaction.emoji) == emojis.check
                    or str(reaction.emoji) in inputdict.keys()
                )

        try:
            reaction, ctx.author = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            # User took too long to respond
            await outmsg.delete()
            return

        # if the reaction isn't the right one, stop.
        if reaction.emoji == emojis.cancel:
            await outmsg.delete()
            return

        if reaction.emoji in inputdict.keys():
            chosen = inputdict[reaction.emoji] - 1
            chosenguild = guildsregisteredin[chosen]

            frompath = paths.guilddbpath / str(chosenguild) / "users" / f"{ctx.author.id}.json"
            topath = paths.guilddbpath / str(ctx.guild.id) / "users" / f"{ctx.author.id}.json"

            topath.parent.mkdir(parents = True, exist_ok = True)

            copyfile(frompath, topath)

            await outmsg.delete()
            await ctx.send(f"Successfully copied profile from *{self.bot.get_guild(int(chosenguild)).name}* to here!")

        else:
            await outmsg.delete()
            raise errors.ThisShouldNeverHappenException


def setup(bot):
    bot.add_cog(RegisterCog(bot))
