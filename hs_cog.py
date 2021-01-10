from discord.ext import commands
from funcs import get_stat
from constants import SKILLS,CLUES,BOSSES,stats_col_names
from getstats import getStats,playerURL
from sql_funcs import sql_update_player_hs , get_all_from_hs,get_players_in_hs,sql_add_player_hs,sql_top_stat,top_stat_to_string,coded_string,is_skill,get_player_stat,get_player_rank,change_player_name,change_player_name_clantracker,change_player_name_mytracker,rm_from_hs
import os
import psycopg2 

class Hiscores(commands.Cog):

    def __init__(self, bot, conn):
        self.bot = bot
        self.conn = conn
        self.cur = conn.cursor()

    @commands.command(name='update', help="Updates a players stats in the clan's hiscores. \n eg: !hs update ironrok r_a_df_o_r_d (updates both players you can do as many as you want)")
    async def update_hs(self,ctx, *members):
        try:
            players = get_players_in_hs(self.cur)
            first_msg = 'Updating '
            for member in members:
                first_msg += f'{member} '
            await ctx.send(first_msg)
            not_found_osrs = []
            not_in_cc = []
            for name in members:
                name = name.lower()
                stats = getStats(playerURL(name,'iron'))
                if stats == 404:
                    not_found_osrs.append(name)
                elif name in players:
                    try:
                        sql_update_player_hs(self.cur,name,stats,stats_col_names)
                        # sql_add_player_hs_historic(self.cur,name,stats)
                        #self.conn.commit()
                    except Exception as e:
                        print(e)
                else:
                    not_in_cc.append(name)
            found = [x for x in members if (x not in not_in_cc and x not in not_found_osrs)]
            response = f"{found} were updated!\n"
            if not_found_osrs:
                response+= f"{not_found_osrs} were not found in the osrs' ironman hiscores.\n"
            if not_in_cc:
                response+= f"{not_in_cc} were not found on the clan's hiscores.\n"
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='ranks', help="Updates a players stats in the clan's hiscores. \n eg: !hs update ironrok r_a_df_o_r_d (updates both players you can do as many as you want)")
    async def ranks_hs(self,ctx, skill, *name):
        try:
            name = ("_").join(name).lower()
            players = get_players_in_hs(self.cur)
            if name in players:
                all_stats = get_all_from_hs(self.cur)
                if skill == "skills":
                    ranks = {}
                    for i,skill in enumerate(SKILLS):
                        all_stats = sorted(all_stats,key=lambda tup: (tup[i*2+1],tup[i*2+2]),reverse=True)
                        index = [x for x, y in enumerate(all_stats) if y[0] == name][0] + 1
                        ranks[skill] = index
                else:
                    ranks = {}
                    for i,stat in enumerate(CLUES+BOSSES,start=49):

                        all_stats = sorted(all_stats,key=lambda tup: tup[i],reverse=True)
                        index = [x for x, y in enumerate(all_stats) if y[0] == name][0]
                        if all_stats[index][i] != -1:
                            ranks[stat] = index + 1
                response = f"{name}\n"
                for skill in ranks:
                    response += f"{skill}: {ranks[skill]}\n"
            else:
                response = f"{name} is not on the clan hs."
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
                    except Exception as e:
                        in_cc.append(name)
            #self.conn.commit()
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
    @commands.has_permissions(kick_members=True)
    async def fullupdate(self,ctx):
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
                except Exception as e:
                    print(str(e))
        response = "Finished updating."
        if not_found_osrs:
            response+= f"{not_found_osrs} were not found in the osrs' hiscores.\n"
            await ctx.send(response)
        
        await ctx.send(response)

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

    @commands.command(name='change2',help="Changes the name in the clan's hiscores.")
    async def change2(self,ctx,old_name,*new_name):
        try:
            players = get_players_in_hs(self.cur)
            new_name = ("_").join(new_name).lower()
            old_name = old_name.lower()
            if old_name in players and new_name not in players:
                change_player_name(self.cur,old_name,new_name)
                change_player_name_clantracker(self.cur,old_name,new_name)
                change_player_name_mytracker(self.cur,old_name,new_name)
                #self.conn.commit()
                response = f"{old_name} changed to {new_name} in the clan's hiscores."
            else:
                response = f"{old_name} not found in the clan's hiscores."

        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='rmoutdated',help="Removes outdated names from the clan's hiscores.")
    async def rmoutdated(self,ctx):
        try:
            await ctx.send("Checking for outdated names in the hs.")
            players_in_hs = get_players_in_hs(self.cur)
            outdated = []
            for name in players_in_hs:
                stats = getStats(playerURL(name,'iron'))
                if stats == 404:
                    outdated.append(name)
                    rm_from_hs(self.cur,name)
            #self.conn.commit()
            response = f"Players outdated and removed: {outdated}"
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='rm',help="Removes names from the clan's hiscores.")
    @commands.has_permissions(kick_members=True)
    async def rm(self,ctx, *members):
        try:
            await ctx.send("Removing players from the hs.")
            players_in_hs = get_players_in_hs(self.cur)
            removed = []
            for name in members:
                name = name.lower()
                if name in players_in_hs:
                    rm_from_hs(self.cur,name)
                    removed.append(name)
            response = f"Players removed: {removed}"
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
    conn.autocommit=True
    bot.add_cog(Hiscores(bot,conn))
