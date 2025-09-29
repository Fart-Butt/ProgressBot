import asyncio
from discord.ext import commands, tasks
import concurrent.futures
import logging

from shared import vacuum_instance as vacuum

log = logging.getLogger('bot.' + __name__)


class ScraperHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.minecraft_scraper_task.start()

    def cog_unload(self):
        self.minecraft_scraper_task.cancel()

    @tasks.loop(seconds=10)
    async def minecraft_scraper_task(self):
        log.debug("MINECRAFT SCRAPER - starting scraper task")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for i in vacuum:
                log.debug("SCRAPER - executing vacuum for guid %s" % i)
                executor.map(vacuum[i].playtime_scraper_rcon())
        log.debug("MINECRAFT SCRAPER - ended")
