import asyncio
import logging
import datetime
import butt_library
from config import command_prefix
import mojang as mj
from butt_library import allowed_in_channel_direct
from discord import Message

from shared import comms_instance, vacuum_instance as vacuum, db, bot

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

    @staticmethod
    async def _process_death_message(message: Message):
        """recieved a notification from the minecraft interface bot that someone died on the server"""
        message_ = butt_library.strip_discord_shitty_formatting(message.content)
        log.debug("PROCESS_DEATH_MESSAGE - message received, %s" % message_)
        if (message.author.id == 249966240787988480 and message_[:4] == 'RIP:') or \
                (message.author.id == 992866467903176765 and message_[:4] == 'RIP:') or \
                (str(message.author) == '💩💩#4048' and message_[:4] == 'RIP:'):
            log.debug("PROCESS_DEATH_MESSAGE - passed author check")
            vacuum[message.guild.id].add_death_message(message_)
        else:
            log.debug("PROCESS_DEATH_MESSAGE - FAILED author check, author id is %s" % str(message.author.id))

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

        if "RIP:" in message.content:
            log.info("CHAT_DISPATCH - GUID %d - message is death alert from game server: %s " % (
                message.guild.id, message.content))
            await self._process_death_message(message)

        elif ("has made the advancement [" in message.content or
              "has reached the goal [" in message.content or
              "has completed the challenge [" in message.content) \
                and message.author.id == 249966240787988480:
            # progress cheevo
            cheevo = db["minecraft"].do_insert(
                "insert into progress.progres_cheevos (`player`, `cheevo_text`, `datetime`, `play_time` ) values (%s, %s, %s, 1)",
                (message.content.split(" ")[0], message.content.split("[")[1][1:-2], datetime.datetime.utcnow())
            )
        elif ("left the server" in message.content or "joined the server" in message.content):
            message_ = butt_library.strip_discord_shitty_formatting(message.content)
            player = message_.split(" ")[0].replace("*",'')
            logging.info("_process_all_other_messages: join/part message from minecraft - %s" % player)
            await self.record_player_guid(player)
            # this is a join or part message and we are going to ignore it
            # welcome to progress
            if message.author.id == 249966240787988480 and "joined the server" in message_:
                log.debug("_process_all_other_messages: starting hwsp for %s" % player)
                hwsp = vacuum[message.guild.id].have_we_seen_player(player)
                log.debug(hwsp)
                if hwsp:
                    log.info("have not seen player before: %s" % player)
                    await self.docomms(hwsp, message.channel, message.guild.id)
            else:
                log.debug(message.author.id)
                log.debug(message_)

    async def record_player_guid(self, player):
        players = db["minecraft"].do_query(
            "select count(player_name) as c from progress.minecraft_players where player_name = %s",
            (player,)
        )
        if players[0]['c'] == 0:
            logging.info("%s is new player, saving to db" % player)
            # we dont see this player in the db, let's record the guid
            db["minecraft"].do_insert("insert into progress.minecraft_players "
                                      "(player_name, player_guid)"
                                      "VALUES (%s, %s)",
                                      (player, self.mojang.mojang_user_to_uuid(player)))
        else:
            # we see this player name in the db, no need to record guid
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
