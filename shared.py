import discord_comms
import butt_database
from config import *
import logging
from discord.ext.commands import Bot
import aiohttp
import asyncio
import discord
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = Bot(description="a bot for Progress", command_prefix=command_prefix, pm_help=False, intents=intents)

log = logging.getLogger('bot.' + __name__)

# database instances
db = {
    "minecraft": butt_database.Db()
}

tables = {
    "previously seen": "previously_seen_players",
    "NSA POI": "NSA_POI",
    "NSA": "NSA_module",
    "deaths": "deaths",
    "playertracker": "playertracker_v2"
}

comms_instance = discord_comms.DiscordComms()

async def create_http_session():
    session = aiohttp.ClientSession()
    return session


http_session = asyncio.get_event_loop().run_until_complete(create_http_session())
