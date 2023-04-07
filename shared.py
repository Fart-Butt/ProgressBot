import discord_comms
import butt_database
from config import *
import logging
import vacuum
from discord.ext.commands import Bot
import aiohttp
import asyncio

bot = Bot(description="a bot for Progress", command_prefix=command_prefix, pm_help=False)

log = logging.getLogger('bot.' + __name__)

# database instances
db = {
    "minecraft": butt_database.Db(minecraft_db, db_secrets[0], db_secrets[1]),
}

tables = {
    "previously seen": "previously_seen_players",
    "NSA POI": "NSA_POI",
    "NSA": "NSA_module",
    "deaths": "deaths",
    "playertracker": "playertracker_v2"
}

comms_instance = discord_comms.DiscordComms()
vacuum_instance = vacuum.VacuumManager()
vacuum_instance.subscribe(154337182717444096, "http://136.32.75.102:8123/up/world/DIM-1/","progress")
vacuum_url = "http://136.32.75.102:8123/up/world/DIM-1/"

async def create_http_session():
    session = aiohttp.ClientSession()
    return session


http_session = asyncio.get_event_loop().run_until_complete(create_http_session())
