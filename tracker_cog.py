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
                    if personal_tracker_starting_stat(self.cur,name,stat,0) == -1:
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
            else:
                response = "You are already being tracked. do: !hs resetmytracker, to restart your tracker. "
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
