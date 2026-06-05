import asyncio
import logging
from config import command_prefix
import mojang as mj
from butt_library import allowed_in_channel_direct
from discord import Message

from shared import comms_instance, bot

log = logging.getLogger('bot.' + __name__)


class ProgressBot:
    def __init__(self):
        self.discordBot = bot
        self.mojang = mj.Mojang()

    @staticmethod
    async def docomms(message, channel, guild_id, bypass_for_test=False):
        """sends a message to a provided discord channel in guild."""
        if allowed_in_channel_direct(guild_id, channel.id) or bypass_for_test is True:
            msg = await comms_instance.do_send_message(channel, message)
            return msg  # returns the message object of the message that was sent to discord

    async def chat_dispatch(self, message: Message):
        log.debug("CHAT_DISPATCH  - GUID %d -  %s " % (
            message.guild.id, message.content))
        try:
            if str(message.content)[0] == command_prefix:
                # command from inside of MC or other game server
                log.debug(
                    "CHAT_DISPATCH  - GUID %d - message is command from game server: %s " % (
                        message.guild.id, message.content))
                await self._process_command_interception(message)
                return
        except IndexError:
            pass

    @staticmethod
    async def _process_command_interception(message: Message):
        """process a command relayed by a bot from in-game."""
        # is this genius? is this not? time will tell.
        try:
            # player, command = message.content.split(command_prefix, 1)
            # remove <> denoting message came from player
            # player = player[1:-2]
            player = message.author.name
            command = message.content.split(command_prefix, 1)[1]
        except IndexError:
            log.debug("_PROCESS_COMMAND_INTERCEPTION - no special character found in message.")
            # no command prefix found in message.
            player = ''
            command = ''
        if command:
            # 5/30/20 - added player sending command as argument to the command so it can be used by commands
            # for personalized processing.
            message.content = "%s%s %s" % (command_prefix, command, player)
            # i wanted to use bot.process_commands here but can't since it explictly filters out bots.  The whole point
            # of this command is to process text sent by bots.
            # I make sure that the commands are only processed by allowed bots in a decorator on the commands themselves
            ctx = await bot.get_context(message)
            await bot.invoke(ctx)
