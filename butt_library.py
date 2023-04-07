from discord.ext.commands import Context, check
from discord import Message
import logging

log = logging.getLogger('bot.' + __name__)


def _should_i_reply_to_bot(ctx: Context):
    """Checks to see if we should reply to message author.  specific to users discord flags as bots"""
    if ctx.message.author.id == 249966240787988480:
        # we should always talk to this bot
        log.debug("SHOULD_I_REPLY_TO_USER: bot check passed")
        return True
    else:
        return False


def should_i_reply_to_user(ctx: Context):
    """master clearinghouse for checking if buttbot should reply to user. checks user block list and accepted bot
    list on a per-guild basis.  also checks global ban list."""
    if ctx.message.author.bot:
        # bot user (flag set by discord server)
        return _should_i_reply_to_bot(ctx)
    else:
        return True


def valid_user_or_bot():
    """makes sure user generating context is a valid to talk to"""

    def predicate(ctx: Context):
        return should_i_reply_to_user(ctx)

    return check(predicate)


def vacuum_enabled_in_guild():
    """makes sure vacuum module is enabled in guild config"""

    def predicate(ctx: Context):
        return True

    return check(predicate)


def can_speak_in_channel():
    """verifies buttbot is allowed to talk in message channel"""

    def predicate(ctx: Context):
        log.debug("CAN_SPEAK_IN_CHANNEL: %s, %d, %s" %
                  (ctx.message.channel.id in [154337182717444096, ],
                   ctx.message.channel.id,
                   "hard coded"))
        return allowed_in_channel(ctx.message)

    return check(predicate)


def allowed_in_channel(message: Message):
    try:
        if message.channel.id in [154337182717444096, ]:
            log.debug("ALLOWED_IN_CHANNEL - True")
            return True
        else:
            log.debug("ALLOWED_IN_CHANNEL - False - %d not in %s" % (
                message.channel.id, 154337182717444096))
            return False
    except IndexError:
        # todo: probably shouldnt happen but we might want to load a config here
        log.error("didnt find config loaded for channel %d in guild %d" % (message.channel.id, message.guild.id))
        return False


def allowed_in_channel_direct(guild: int, channel: int):
    try:
        if channel in [154337182717444096, ]:
            return True
        else:
            return False
    except IndexError:
        # todo: probably shouldnt happen but we might want to load a config here
        log.error("didnt find config loaded for channel %d in guild %d" % (channel, guild))
        return False


def strip_discord_shitty_formatting(message: str):
    if message[:2] == "**":
        return message[2:-2]
    elif message[:1] == "_":
        return message[1:-1]
    else:
        return message
