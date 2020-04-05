import asyncio

from discord.ext import commands
from sizebot.discordplus import commandsplus

from sizebot.lib.constants import emojis

inputdict = {
    "1️⃣": "1",
    "2️⃣": "2",
    "3️⃣": "3",
    "4️⃣": "4",
    "5️⃣": "5",
    "6️⃣": "6",
    "7️⃣": "7",
    "8️⃣": "8",
    "9️⃣": "9",
    "0️⃣": "0"
}


class KeypadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commandsplus.command(
        hidden = True
    )
    async def keypad(self, ctx):
        """Test keypad command."""
        author = ctx.author
        defaultmessage = f"**Input:**{emojis.blank}"

        outputmsg = await ctx.send(defaultmessage)

        def check(reaction, reacter):
            return reaction.message.id == outputmsg.id \
                and reacter.id == author.id \
                and (str(reaction.emoji) in inputdict.keys()
                     or str(reaction.emoji) == emojis.cancel)

        for emoji in inputdict.keys():
            await outputmsg.add_reaction(emoji)
        await outputmsg.add_reaction(emojis.cancel)

        listening = True

        while listening:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                # User took too long to respond
                listening = False
                break

            if str(reaction.emoji) in inputdict.keys():
                await outputmsg.edit(content = outputmsg.content + inputdict[str(reaction.emoji)])
                await reaction.remove(user)
            if str(reaction.emoji) == emojis.cancel:
                await outputmsg.edit(content = defaultmessage)
                await reaction.remove(user)

        await outputmsg.clear_reactions()


def setup(bot):
    bot.add_cog(KeypadCog(bot))
