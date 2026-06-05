import asyncio
import random as rand
import shared


class DiscordComms:
    def __init__(self):
        pass

    @staticmethod
    async def do_send_message(channel, message):
        # this shit sends the messages to the peeps
        await asyncio.sleep(2)
        async with channel.typing():
            await asyncio.sleep(rand.randint(2, 5))
            msg = await channel.send(message)  # dont remove await from here or this shit will break
            return msg