import logging
from discord.ext.commands import Bot, Cog, Context, command, BucketType
from discord.ext import commands
from shared import db
import mojang
import datetime
import random
import asyncio
from butt_library import valid_user_or_bot, vacuum_enabled_in_guild, can_speak_in_channel

log = logging.getLogger('bot.' + __name__)


class VacuumCog(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def registerbase(self, ctx: Context, *args):
        """register your minecraft base with buttbot.  this will automatically update your previous entry."""
        db["minecraft"].do_insert("insert into progress_NSA_POI (player, dimension, poi_estimated_size, x, z, datetime)"
                                  " select * from (select player, dimension, 100 as poi_estimated_size, x, z, datetime "
                                  "from progress_NSA_module where player = %s order by datetime DESC limit 1) as new "
                                  "on duplicate key update datetime = new.datetime, x = new.x, z = new.z", (args[0],))
        async with ctx.typing():
            await asyncio.sleep(4)
        await ctx.send("your butt is now registered with buttbot")

    @command()
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def whosebase(self, ctx: Context, *args):
        """reports whose base you are standing in."""
        # this query checks to see if someone has the base registered in the database.
        requester = args
        a = db["minecraft"].do_query("select pnp.player from progress_NSA_POI pnp "
                                     "left join (select x, z from progress_NSA_module "
                                     "where player = %s group by datetime DESC limit 1) t1 "
                                     "on pnp.x between (t1.x-60) and (t1.x+60) "
                                     "where pnp.z between (t1.z-60) and (t1.z+60)", (requester,))

        players = len(a)
        if players > 0:
            # 1 or more players registered at this location
            player = list()
            for lines in a:
                player.append(lines['player'])
            message = "%s lives there" % ", ".join(player)
        else:
            # no one registered at this location, lets poll the tracking table to see who is likely
            b = db["minecraft"].do_query("select player, count(*) as co, "
                                         "count(*) / (select count(*) from progress_NSA_module pnm left join "
                                         "(select x, z from progress_NSA_module where player = %s "
                                         "group by datetime DESC limit 1) t1 on "
                                         "pnm.x between (t1.x-50) and (t1.x+50) "
                                         "where pnm.z between (t1.z-50) and (t1.z+50))*100 as percent "
                                         "from progress_NSA_module pnm left join "
                                         "(select x, z from progress_NSA_module where "
                                         "player = %s group by datetime DESC limit 1) t1 "
                                         "on pnm.x between (t1.x-50) and (t1.x+50) where "
                                         "pnm.z between (t1.z-50) and (t1.z+50) "
                                         "group by player "
                                         "having percent > 15 and co > 1000", (requester, requester))
            if len(b) > 0:
                # someone probably lives here
                player = list()
                for lines in b:
                    player.append(lines['player'])
                message = "i think %s might live there" % ", ".join(player)
            else:
                # no one lives here??
                message = "I think no one lives there"
        async with ctx.typing():
            await asyncio.sleep(4)
        await ctx.send(message)

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def gaminggods(self, ctx: Context):
        """lets you know who is boss"""
        result = db["minecraft"].do_query(
            """select ppv.player, format(sum(ppv.timedelta)/60/60, 1) as time
            from progress_playertracker_v2 ppv
            inner join
                (select T.player FROM progress_playertracker_v2 as T
                    left join(SELECT count(D.player) as deaths, D.player from progress_deaths D GROUP BY D.player) D
                ON T.player = D.player where coalesce(deaths,0) = 0 and T.datetime > DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            group by player
            having sum(T.timedelta) > 18000) t1
            on ppv.player = t1.player
            group by player
            order by time DESC"""
        )
        if len(result) > 1:
            # normal return
            async with ctx.typing():
                await asyncio.sleep(4)
            await ctx.send("here are your gaming gods: %s" % self.sort(result, 'player', 'time', " hours"))
        elif len(result) == 1:
            async with ctx.typing():
                await asyncio.sleep(4)
                comments = ["https://www.youtube.com/watch?v=wubnFmYYfHs",
                            "https://www.youtube.com/watch?v=iLBBRuVDOo4",
                            "https://media.giphy.com/media/JoV2BiMWVZ96taSewG/giphy.gif",
                            "https://www.youtube.com/watch?v=m1xs14LwzBM"
                            ]
                r = comments[random.randrange(0, len(comments)) - 1]
            await ctx.send("only %s is left. %s" % (result[0]['player'], r))
        else:
            async with ctx.typing():
                await asyncio.sleep(4)
            await ctx.send("this world is without any gaming gods")
            # no one left

    @command()
    @commands.cooldown(1, 2, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def lastseen(self, ctx: Context, *args):
        """i wonder where they went?"""
        log.debug("LASTSEEN - arguments are %s" % args)
        try:
            player = args[0]
            if player:
                lastseen = db["minecraft"].do_query(
                    "select datetime from progress_playertracker_v2 "
                    "where player=%s order by datetime desc limit 1",
                    (player,)
                )
                db["minecraft"].close()
                try:
                    lastseen = lastseen[0]['datetime']
                    now = datetime.datetime.utcnow()

                    timedelta = now - lastseen
                    seconds = abs(timedelta.total_seconds())
                    if seconds > 15:
                        days, remainder = divmod(seconds, 86400)
                        hours, remainder = divmod(remainder, 3600)
                        async with ctx.typing():
                            await asyncio.sleep(3)
                        await ctx.send('last saw %s %s days %s hours ago' % (player, int(days), int(hours)))
                    else:
                        async with ctx.typing():
                            await asyncio.sleep(3)
                        await ctx.send("Did you remember to wear your helmet today, honey?")
                except IndexError:
                    async with ctx.typing():
                        await asyncio.sleep(3)
                    await ctx.send("Havent seen em")
        except IndexError:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("who am i looking for?")

    @command()
    @commands.cooldown(1, 2, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def playtime(self, ctx: Context, *args):
        """watch the muscle atrophy in real time"""
        try:
            player = args[0]
            if player:
                returnz = self.playtime_insult(player, ctx.message.guild.id)
                if returnz:
                    async with ctx.typing():
                        await asyncio.sleep(3)
                    await ctx.send(returnz)
            else:
                async with ctx.typing():
                    await asyncio.sleep(3)
                await ctx.send(self.playtime_global(ctx.message.guild.id))
        except IndexError:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send(self.playtime_global(ctx.message.guild.id))

    @staticmethod
    def playtime_global(guild_guid: int):
        players = db["minecraft"].do_query(
            "select abs(sum(timedelta)) as seconds, count(timedelta)"
            " as sessions, player from progress_playertracker_v2 group by player"
        )
        db["minecraft"].close()
        total_seconds = 0
        total_sessions = 0
        for p in players:
            total_seconds = total_seconds + int(p['seconds'])
            total_sessions = total_sessions + p['sessions']
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        return ("These fucking nerds have played %s days, %s hours worth of meincraft over %s sessions" % (
            days, hours, total_sessions))

    @staticmethod
    def playtime_single(player: str, guild_guid: int):
        time = db["minecraft"].do_query(
            "select sum(progress_playertracker_v2.timedelta) as seconds, "
            "count(progress_playertracker_v2.timedelta) as sessions "
            "from progress_playertracker_v2 where player in "
            "(select player_name from progress.minecraft_players "
            "where player_guid = (select player_guid as guid from progress.minecraft_players where player_name = %s))"
            , (player,))
        return [time[0]['seconds'], time[0]['sessions']]

    def playtime_insult(self, player: str, guild_guid: int):
        a = self.playtime_single(player, guild_guid)
        totaltime = a[0]
        sessions = a[1]
        if not totaltime == 0:
            m, s = divmod(totaltime, 60)
            h, m = divmod(m, 60)
            insult = ""
            if h > 1000:
                insult = ". i found kurr lol"
            elif h > 150:
                insult = ". why are you still so bad at this game"
            elif h > 80:
                insult = ". is this shit your full time job or something"
            elif h > 50:
                insult = ". go outside you fuckin nerd"
            elif h > 30:
                insult = ". don't you have something better to do with your time?"
            elif h < 25:
                insult = ". weak"

            return "Estimated playtime for %s: %d hours %d minutes in %s sessions%s" % (player, h, m, sessions, insult)
        else:
            return "bitch dont play"

    def howchies_profile(self, message: str, guild_guid: int):
        result = db["minecraft"].do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` where match(message) against (%s)"
            "GROUP BY player ORDER by count DESC",
            (message,))
        db["minecraft"].close()
        if result:
            return self.sort(result, 'player', 'count')
        else:
            return 'No deaths recorded'

    def ouchies_profile(self, player: str, guild_guid: int):
        result = db["minecraft"].do_query(
            "SELECT message,count(*) as `count` FROM `progress_deaths` WHERE player=%s"
            " GROUP BY message ORDER BY count DESC",
            (player,))
        db["minecraft"].close()
        if result:
            return self.sort(result, 'message', 'count')
        else:
            return 'No deaths recorded'

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def howchies(self, ctx: Context, *args):
        """here's whats killing you"""
        log.debug("HOWCHIES - triggered")
        if args:
            r = self.howchies_profile(args[0], ctx.message.guild.id)
            log.debug("HOWCHIES - search mode - returned: 'people who died to %s: %s" % (" ".join(args), r))
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("People who died to %s: %s" % (args, r))
        else:
            r = self.top_10_death_reasons(ctx.message.guild.id)
            log.debug("HOWCHIES - top 10 - returned: %s" % r)
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("Heres whats killing you: %s" % r)

    def top_10_death_reasons(self, guild_guid: int):
        result = db["minecraft"].do_query(
            "SELECT message, count(*) as `count` FROM `progress_deaths` "
            "GROUP BY message ORDER BY count DESC LIMIT 10",
            '')
        if result:
            return self.sort(result, 'message', 'count')
        else:
            pass

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def ouchies(self, ctx: Context, *args):
        """reflect upon the dead"""
        log.debug("ouchies ")
        try:
            if args[0]:
                r = self.ouchies_profile(args[0], ctx.message.guild.id)
                log.debug("OUCHIES - player search - searched %s, returned: %s" % (args[0], r))
                async with ctx.typing():
                    await asyncio.sleep(3)
                await ctx.send("Deaths for %s: %s" % (args[0], r))
                return
        except IndexError:
            # no args, lets do top 10
            r = self.top_10_deaths(ctx.message.guild.id)
            log.debug("OUCHIES - top 10 - returned: %s" % r)
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send('Top 10 ouchies: %s' % r)

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def alias(self, ctx: Context, *args):
        """sneaky playerses"""
        names = self.player_alias(args[0])
        log.debug("ALIAS - searching player")
        if len(names) == 0:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("I dont think i've ever seen that person")
        elif len(names) == 1:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("I've only seen this person as %s" % names[0])
        else:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("I've seen this person play as %s" % ", ".join(names))

    def top_10_deaths(self, guild_guid: int):
        result = db["minecraft"].do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` GROUP BY player ORDER BY count DESC LIMIT 10")
        if result:
            return self.sort(result, 'player', 'count')
        else:
            pass

    def deathsperhour_list(self, guild_guid: int):
        dph = db["minecraft"].do_query(
            "select T.player, COALESCE(D.deaths, 0) / (sum(T.timedelta) / 60 / 60) as deaths_per_hour"
            "FROM progress_playertracker_v2 as T left join(SELECT count(D.player) as deaths, "
            "D.player from {0}_deaths D GROUP BY D.player) D ON T.player = D.player group by"
            "T.player ORDER BY deaths_per_hour DESC LIMIT 10"
        )
        if dph:
            return self.sort(dph, 'player', 'deaths_per_hour')

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def deathsperhour(self, ctx: Context, *args):
        dph = db["minecraft"].do_query(
            "select T.player, COALESCE(D.deaths, 0) / format((sum(T.timedelta)/60/60),1) as deaths_per_hour FROM "
            "progress_playertracker_v2 as T left join (SELECT count(D.player) as deaths, D.player"
            " from progress_deaths D where player=%s GROUP BY D.player) D"
            " ON T.player = D.player where T.player=%s group by T.player", (args[0], args[0]))
        try:
            if dph[0]['deaths_per_hour'] > 0:
                # good return
                if dph[0]['deaths_per_hour'] > 5:
                    insults = [
                        "my hero",
                        "a true gaming legend"
                    ]
                    insult = insults[random.randrange(0, len(insults) - 1)]

                else:
                    insult = "you should try harder"
                log.debug("DEATHSPERHOUR - deaths per hour for %s is %s. %s" %
                          (args[0],
                           str(dph[0]['deaths_per_hour']),
                           insult))
                async with ctx.typing():
                    await asyncio.sleep(3)
                await ctx.send("deaths per hour for %s is %s. %s" %
                               (args[0],
                                str(dph[0]['deaths_per_hour']),
                                insult))
            else:
                comments = [
                    "%s is the most boring person on the server",
                    "actually, %s is just a gaming god",
                    "persistence is key for %s",
                    "%s is a god among mortals"
                ]
                r = comments[random.randrange(0, len(comments)) - 1] % args[0]
                log.debug("DEATHSPERHOUR - %s" % r)
                async with ctx.typing():
                    await asyncio.sleep(3)
                await ctx.send(r)
        except IndexError:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send("%s doesnt play" % args[0])

    @staticmethod
    def player_alias(player):
        db["minecraft"].build()
        r = db["minecraft"].do_query("select player_name from minecraft_players where player_guid ="
                                     " (select player_guid as guid from minecraft_players where player_name = %s)",
                                     (player,))
        names = []
        for re in r:
            names.append(re['player_name'])
        return names

    @staticmethod
    def sort(target, t1, t2, t3=""):
        cmsg = ''
        i = 1
        for d in target:
            if i != 1:
                cmsg = cmsg + ', '
            cmsg = cmsg + d[t1] + "(%s%s)" % (str(d[t2]), t3)
            i = i + 1
        return cmsg

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def uuid(self, ctx: Context, *args):
        a = mojang.Mojang
        uid = a.mojang_user_to_uuid(args[0])
        async with ctx.typing():
            await asyncio.sleep(3)
        await ctx.send("uuid is %s" % str(uid))

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def basewaypoint(self, ctx: Context, *args):
        """will give you a waypoint for a registered player's base"""
        requester = args
        a = db["minecraft"].do_query("select x, z, player from progress.progress_NSA_POI where player=%s", (requester,))

        players = len(a)
        if players > 0:
            # 1 or more players registered at this location
            player = list()
            for lines in a:
                player.append(lines['player'])
            message = '[name:"Home of %s", x:%s, y:64, z:%s, dim:minecraft:overworld]' % \
                      (", ".join(player),
                       a[0]['x'],
                       a[0]['z'])
        else:
            message = "this player does not have their base registered with buttbot"
        print(message)
        async with ctx.typing():
            await asyncio.sleep(3)
        await ctx.send(message)

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @vacuum_enabled_in_guild()
    @can_speak_in_channel()
    async def cheevo(self, ctx: Context, *args):
        """returns cheevo info for a specified cheevo"""
        cheevo = " ".join(args)
        a = db["minecraft"].do_query('''select o.oldest, n.newest, p.percent_players from
            (select player as oldest from progress.progres_cheevos where cheevo_text = %s order by datetime asc limit 1) as o,
            (select player as newest from progress.progres_cheevos where cheevo_text = %s order by datetime desc limit 1) as n,
            (select ch.total_w_cheevo/ppv.total_players*100 as percent_players from
            (select count(distinct player) total_players from progress.progress_playertracker_v2) as ppv,
            (select count(distinct player) as total_w_cheevo from progress.progres_cheevos where cheevo_text = %s) as ch) as p''',
                                     (cheevo, cheevo, cheevo))
        print(a)
        message = "first post: {}  most recent: {}  %of players with achievement: {:.0f}%".format(a[0]['oldest'],
                                                                                                  a[0]['newest'],
                                                                                                  a[0][
                                                                                                      'percent_players'])
        async with ctx.typing():
            await asyncio.sleep(3)
        await ctx.send(message)
