import asyncio
from pathlib import Path
import datetime
import aiohttp
from cogs.vacuum import VacuumCog
from cogs.scraper_handler import ScraperHandler
from progress import ProgressBot
from shared import bot, vacuum_instance
from discord.channel import DMChannel
import logging
from discord.ext import tasks

import config

LOGDIR = Path('logs')


def setup_logger() -> logging.Logger:
    """Create and return the master Logger object."""
    LOGDIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    logfile = LOGDIR / f'{timestamp}.log'
    logger = logging.getLogger('bot')  # the actual logger instance
    logger.setLevel(logging.DEBUG)  # capture all log levels
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)  # log levels to be shown at the console
    file_log = logging.FileHandler(logfile)
    file_log.setLevel(logging.INFO)  # log levels to be written to file
    formatter = logging.Formatter('{asctime} - {name} - {levelname} - {message}', style='{')
    console_log.setFormatter(formatter)
    file_log.setFormatter(formatter)
    logger.addHandler(console_log)
    logger.addHandler(file_log)
    return logger


log = setup_logger()
progressbot = ProgressBot()


@bot.event
async def on_ready():
    log.info('Use this link to invite {}:'.format(bot.user.name))
    log.info('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(bot.user.id))
    log.info('--------')
    log.info('You are running progressbot 1')
    log.info('Created by Poop Poop')
    log.info('--------')


@bot.event
async def on_message(message):
    if isinstance(message.channel, DMChannel):
        # we don't care about this
        pass
    else:
        if message.author == bot.user:
            # me
            return
        if message.channel.id == 154337182717444096:
            try:
                print("message author: %s" % message.author.id)
                if message.content[0] == config.command_prefix:
                    if message.author.id != 249966240787988480:
                        log.debug(
                            "MAIN - ON_MESSAGE - sending message to command processor - author %s" % str(
                                message.author.id))
                        await bot.process_commands(message)
                    else:
                        log.debug("MAIN - ON_MESSAGE - progress detected.")
                        await progressbot.chat_dispatch(message)
                else:
                    # send to message processor
                    await progressbot.chat_dispatch(message)
            except IndexError:
                # also send
                await progressbot.chat_dispatch(message)


async def main():
    # do other async things
    # start the client
    async with bot:
        log.debug("MAIN - starting")
        await bot.add_cog(ScraperHandler(bot))
        log.debug("MAIN - progressbot scraper started")
        await bot.add_cog(VacuumCog(bot))
        bot.aiohttp_session = aiohttp.ClientSession()
        log.debug("MAIN - starting bot")
        await bot.start(config.secretkey)


asyncio.run(main())
