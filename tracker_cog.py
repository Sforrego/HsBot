from discord.ext import commands
from getstats import *
from funcs import *
from sql_funcs import *
import os

class Tracker(commands.Cog):

    def __init__(self, bot, conn):
        self.bot = bot
        self.conn = conn
        self.cur = conn.cursor()

    @commands.command(name='addtotracker', help="Adds a players to clan tracker. \n eg: !hs addtotracker ironrok its_ruhspect")
    async def start_clan_tracker(self,ctx,*members):
        try:
            await ctx.send("Adding players to the tracker.")
            players = get_players_in_tracker(self.cur)
            already_being_tracked = []
            not_found_osrs = []
            for name in members:
                name = name.lower()
                if name in players:
                    already_being_tracked.append(name)
                else:
                    stats = getStats(playerURL(name,'iron'))
                    if stats == 404:
                        not_found_osrs.append(name)
                    else:
                        sql_update_player_hs(self.cur,name,stats,stats_col_names)
                        add_clan_tracker(self.cur,name,stats)
            self.conn.commit()
            response = ''
            if already_being_tracked:
                response += f'{already_being_tracked} are already being tracked.\n'
            if not_found_osrs:
                response += f'{not_found_osrs} were not found in the osrs hiscores.\n'
            found = [x for x in members if (x not in already_being_tracked and x not in not_found_osrs)]
            response += f'{found} were added to the clan tracker.'
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)


    @commands.command(name='checktracker', help="Checks a players progress according to the clan tracker. \n eg: !hs checktracker ironrok Mining")
    async def check_clan_tracker(self,ctx,name,stat):
        try:
            name = name.lower()
            clan_tracker_names = get_players_in_clan_tracker(self.cur)
            if name in clan_tracker_names:
                if stat:
                    stat = ("_").join(stat).lower()
                    pretty_stat = get_stat(stat)
                    stat = coded_string(pretty_stat)
                else:
                    stat = "overall"
                    pretty_stat = "Overall"
                skill = is_skill(stat)
                if skill:
                    stat_delta,time_delta = xp_gained_clan(self.cur,name,stat,skill)
                    hours,mins = seconds_to_hours_mins(time_delta.seconds)
                    response = f"{name} has gained {str(stat_delta)} {pretty_stat} xp in the last {time_delta.days}d {hours}h {mins}m."
                else:
                    if tracker_starting_stat(self.cur,name,stat,0,'clan_tracker') == -1:
                        response = f"{name} starting {pretty_stat} was not ranked in the hs."
                    else:
                        stat_delta,time_delta = xp_gained_clan(self.cur,name,stat,skill)
                        hours,mins = seconds_to_hours_mins(time_delta.seconds)
                        response = f"{name} has done {str(stat_delta)} {pretty_stat} kills in the last {time_delta.days}d {hours}h {mins}m."

            else:
                response = f"{name} is not in the clan tracker."
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='toptracker', help="Checks the top 5 progress according to the clan tracker in a stat. \n eg: !hs toptracker mining")
    async def toptracker(self,ctx,stat):
        skill = is_skill(stat)
        top = top_stat_to_string(top_tracked(self.cur,stat,skill,5))
        response = f'```\n{top}```'
        await ctx.send(response)
    @commands.command(name='toptracker10', help="Checks the top 5 progress according to the clan tracker in a stat. \n eg: !hs toptracker mining")
    async def toptracker(self,ctx,stat):
        top = top_stat_to_string(top_tracked(self.cur,stat,skill,10))
        response = f'```\n{top}```'
        await ctx.send(response)

    @commands.command(name='resetclantracker',help='Removes everyone from the clantracker')
    async def resettracker(self,ctx):
        self.cur.execute("delete from clan_tracker")
        self.conn.commit()
        await ctx.send('Clan tracker reset.')

    @commands.command(name='startmytracker', help="Starts a player's personal tracker. \n eg: !hs startmytracker")
    async def start_my_tracker(self,ctx):
        try:
            name = coded_string(ctx.message.author.display_name)
            personal_tracker_names = get_players_in_personal_tracker(self.cur)
            if name not in personal_tracker_names:
                stats = getStats(playerURL(name,'iron'))
                if stats == 404:
                    response = f"{name} is not on the osrs hiscores."
                else:
                    add_personal_tracker(self.cur,name,stats)
                    sql_update_player_hs(self.cur,name,stats,stats_col_names)
                    self.conn.commit()
                    response = f"You are now being tracked. use !hs update 'your_name' to update your stats and !hs mytracker 'skill' to check your progress."
            else:
                response = "You are already being tracked. do: !hs resetmytracker, to restart your tracker. "
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='mytracker', help="Check's xp/kills gained since being tracked with the personal tracker. \n eg: !hs mytracker hunter")
    async def my_tracker(self,ctx,*stat):
        try:
            name = coded_string(ctx.message.author.display_name)
            personal_tracker_names = get_players_in_personal_tracker(self.cur)
            if name in personal_tracker_names:
                if stat:
                    stat = ("_").join(stat).lower()
                    pretty_stat = get_stat(stat)
                    stat = coded_string(pretty_stat)
                else:
                    stat = "overall"
                    pretty_stat = "Overall"
                skill = is_skill(stat)

                if skill:
                    stat_delta,time_delta = xp_gained(self.cur,name,stat,skill)
                    hours,mins = seconds_to_hours_mins(time_delta.seconds)
                    response = f"{name} has gained {str(stat_delta)} {pretty_stat} xp in the last {time_delta.days}d {hours}h {mins}m."
                else:
                    if tracker_starting_stat(self.cur,name,stat,0,'personal_tracker') == -1:
                        response = f"Your starting {pretty_stat} was not ranked in the hs, if it is now you could do !hs resetmytracker to reset your tracker."
                    else:
                        stat_delta,time_delta = xp_gained(self.cur,name,stat,skill)
                        hours,mins = seconds_to_hours_mins(time_delta.seconds)
                        response = f"{name} has done {str(stat_delta)} {pretty_stat} kills in the last {time_delta.days}d {hours}h {mins}m."

            else:
                response = "You are not being tracked, to start your tracker do !hs startmytracker"


        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='resetmytracker', help="Resets a player's personal tracker'. \n eg: !hs resetmytracker")
    async def reset_my_tracker(self,ctx):
        try:
            name = coded_string(ctx.message.author.display_name)
            personal_tracker_names = get_players_in_personal_tracker(self.cur)
            if name in personal_tracker_names:
                stats = getStats(playerURL(name,'iron'))
                if stats == 404:
                    response = f"{name} is not on the osrs hiscores."
                else:
                    reset_personal_tracker(self.cur,name)
                    add_personal_tracker(self.cur,name,stats)
                    sql_update_player_hs(self.cur,name,stats,stats_col_names)
                    self.conn.commit()
                    response = f"Your tracker has been reset!"
            else:
                response = "You are not being tracked, to start your tracker do !hs startmytracker"
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)






def setup(bot):
    # user = os.getenv('user')
    # password = os.getenv('password')
    # host = os.getenv('host')
    # port = os.getenv('port')
    # database = os.getenv('database')
    # conn = psycopg2.connect(user=user,password=password,host=host,port=port,database=database)

    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    bot.add_cog(Tracker(bot,conn))
