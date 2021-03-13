import logging

import arrow
from mongoengine import Document
from mongoengine.fields import IntField

from sizebot.lib.db import ArrowField

logger = logging.getLogger("sizebot")


class Nanny(Document):
    userid = IntField(required=True)
    guildid = IntField(required=True, unique_with="userid")
    endtime = ArrowField(required=True)

    async def tuckin(self, bot):
        guild = await bot.fetch_guild(self.guildid)
        # If the bot doesn't have permission to kick users from a voice channel, give up on this nap
        # if not guild.me.guild_permissions.move_members:
        bot_member = await guild.fetch_member(bot.user.id)
        if not bot_member.guild_permissions.move_members:
            logger.info("I do not have permission to move users in this guild.")
            self.delete()
            return
        member = await guild.fetch_member(self.userid)
        # PERMISSION: requires move_members
        logger.info(f"Dragging {member} to bed.")
        await member.move_to(None, reason="Naptime!")
        self.delete()

    def __str__(self):
        userid, guildid, endtime = self.userid, self.guildid, self.endtime
        return f"Nap({userid=}, {guildid=}, {endtime=})"


def get_nannies():
    return Nanny.objects


def schedule(userid, guildid, durationTV):
    """Start a new naptime nanny"""
    endtime = arrow.now().shift(seconds=float(durationTV))
    nanny = Nanny(userid=userid, guildid=guildid, endtime=endtime)
    nanny.save()


def cancel(userid, guildid):
    """Stop a waiting naptime nanny"""
    nanny = Nanny.objects(userid=userid, guildid=guildid).first()
    if nanny is not None:
        nanny.delete()
    return nanny


async def check(bot):
    """Have the nannies check their watches"""
    nannies = Nanny.objects(endtime__gte=arrow.now())
    for nanny in nannies:
        await nanny.tuckin(bot)
