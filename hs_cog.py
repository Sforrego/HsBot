from discord.ext import commands
from getstats import *
from funcs import *
from sql_funcs import *
import os

class Hiscores(commands.Cog):

    def __init__(self, bot, conn):
        self.bot = bot
        self.conn = conn
        self.cur = conn.cursor()


    @commands.command(name='update', help="Updates a players stats in the clan's hiscores. \n eg: !hs update ironrok r_a_df_o_r_d (updates both players you can do as many as you want)")
    async def update_hs(self,ctx, *members):
        try:
            first_msg = 'Updating '
            for member in members:
                first_msg += f'{member} '
            await ctx.send(first_msg)
            not_found_osrs = []
            sth_wrong = []
            for name in members:
                stats = getStats(playerURL(name,'iron'))
                if stats == 404:
                    not_found_osrs.append(name)
                else:
                    try:
                        sql_update_player_hs(self.cur,name,stats_col_names,stats)
                        sql_add_player_hs_historic(self.cur,name,stats)
                    except Exception as e:
                        sth_wrong.append(name)
            self.conn.commit()
            found = [x for x in members if (x not in sth_wrong and x not in not_found_osrs)]
            response = f"{found} were updated!"
            if not_found_osrs:
                response+= f"{not_found_osrs} were not found in the osrs' hiscores.\n"
            if sth_wrong:
                response+= f"{sth_wrong} were not found on the clan's hiscores.\n"
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='add', help="Adds players to the clan's hiscores. \n eg: !hs addhs ironrok r_a_df_o_r_d (updates both players you can do as many as you want)")
    @commands.has_permissions(kick_members=True)
    async def add_hs(self,ctx, *members):
        try:
            first_msg = 'Adding '
            for member in members:
                first_msg += f'{member} '
            first_msg += "to the clan's hs."
            await ctx.send(first_msg)
            not_found_osrs = []
            in_cc = []
            all_names = get_players_in_hs(self.cur)
            for name in members:
                name = name.lower()
                stats = getStats(playerURL(name,'iron'))
                if stats == 404:
                    not_found_osrs.append(name)
                elif name in all_names:
                    in_cc.append(name)
                else:
                    try:
                        sql_add_player_hs(self.cur,name,stats)
                        sql_add_player_hs_historic(self.cur,name,stats)
                    except Exception as e:
                        in_cc.append(name)
            self.conn.commit()
            found = [x for x in members if (x not in in_cc and x not in not_found_osrs)]
            response = f"{found} were added!\n"
            if not_found_osrs:
                response+= f"{not_found_osrs} were not found in the osrs' hiscores.\n"
            if in_cc:
                response+= f"{in_cc} these players are already in the clan's hiscores.\n"
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)


    @commands.command(name='top', help="Shows the top 5 players and their kc/lvl+xp for a specific stat.")
    async def top_hs(self,ctx, *stat):

        try:
            response = "```\n"
            stat = ("_").join(stat).lower()
            stat_pretty = get_stat(stat)
            stat = coded_string(stat_pretty)

            response += f"{stat_pretty}\n"
            skill = is_skill(stat)
            result = sql_top_stat(self.cur,stat,5,skill,stats_col_names)
            response += top_stat_to_string(result)
            response += "```"
        except Exception as e:
            response = str(e)
        finally:
            print(response)
            await ctx.send(response)

    @commands.command(name='top10', help="Shows the top 10 players and their kc/lvl+xp for a specific stat.")
    async def top10_hs(self,ctx, *stat):

        try:
            response = "```\n"
            stat = ("_").join(stat).lower()
            stat_pretty = get_stat(stat)
            stat = coded_string(stat_pretty)

            response += f"{stat_pretty}\n"
            skill = is_skill(stat)
            result = sql_top_stat(self.cur,stat,10,skill,stats_col_names)
            response += top_stat_to_string(result)
            response += "```"
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)


    @commands.command(name='check', help="Checks if a player is in the clan's hs.")
    async def check_hs(self,ctx, name):
        name = name.lower()
        players = get_players_in_hs(self.cur)
        if name in players:
            response = f"{name} is in the clan's hiscores."
        else:
            response = f"{name} is not in the clan's hiscores."

        await ctx.send(response)

    @commands.command(name='my', help="Gets the person using the command lvl/kc in a stat.")
    async def my_hs(self,ctx, *stat):

        try:
            stat = ("_").join(stat).lower()
            name = coded_string(ctx.message.author.display_name)
            stat = coded_string(get_stat(stat))
            skill = is_skill(stat)
            result = get_player_stat(self.cur,name,stat,skill,stats_col_names)[0]
            if skill:
                response = f"{name}'s {stat} level: {result[1]} with {result[2]} xp."
            else:
                response = f"{name}'s {stat} kc: {result[1]}."

        except Exception as e:
            response = e
        finally:
            await ctx.send(response)

    @commands.command(name='fullupdate', help="Updates every player in the clan's hiscores.")
    async def fullupdate(ctx):
        await ctx.send("Updating all players...")
        members = get_players_in_hs(self.cur)
        not_found_osrs = []
        for name in members:
            stats = getStats(playerURL(name,'iron'))
            if stats == 404:
                not_found_osrs.append(name)
            else:
                try:
                    sql_update_player_hs(self.cur,name,stats_col_names,stats)
                    sql_add_player_hs_historic(self.cur,name,stats)
                except Exception as e:
                    in_cc.append(name)
        self.conn.commit()

        if not_found_osrs:
            response+= f"{not_found_osrs} were not found in the osrs' hiscores.\n"
            await ctx.send(response)

        await ctx.send("Finished updating.")


    @commands.command(name='rank', help='Shows the rank within the clan of a member in a specific stat. (!hs rank zulrah spniz_uim)')
    async def ranks(self,ctx,stat,name):
        try:
            name = name.lower()
            stat_pretty = get_stat(stat.lower())
            stat = coded_string(stat_pretty)
            names = get_players_in_hs(self.cur)
            if name in names:
                skill = is_skill(stat)
                rank = get_player_rank(self.cur,name,stat,skill)
                response = f"{name} is rank {rank} in {stat_pretty}"
            else:
                response = f"{name} is not on the clan's hiscores."


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

    bot.add_cog(Hiscores(bot,conn))
