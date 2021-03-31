import discord
import gspread
import os 
import psycopg2
from discord.ext import commands
from constants import TILES_TO_NUM, stats_col_names #, BINGO_HIDDEN
from funcs import complete_tile,get_number_tiles_left, get_tiles_done,reveal_tile,undo_tile,get_tiles_left
from sql_funcs import get_team_nums, add_team, get_team, update_team,xp_gained_team,tracker_starting_stat_multiple,is_skill,coded_string,get_stat,reset_teams,sql_update_player_hs
from random import random,randint
from image_editing import paint_tiles
from getstats import getStats, playerURL
from oauth2client.service_account import ServiceAccountCredentials


class Bingo(commands.Cog):
    def __init__(self, bot, conn, client, bingo_sheet_tiles):
        self.conn = conn
        self.cur = conn.cursor()    
        self.client = client
        self.bingo_sheet_tiles = bingo_sheet_tiles

    @commands.command(name='complete', help='Completes a Tile.')
    @commands.has_permissions(kick_members=True)
    async def complete(self,ctx, team_num, *tile_name):
        try:
            self.bingo_sheet_tiles.col_values(1)
        except gspread.exceptions.APIError:
            self.client.login()
        tile_name = " ".join(tile_name)
        tile_name = tile_name.lower()
        team_num = int(team_num)
        if team_num not in range(1,9):
            response = "You need to specify the number of your team\n !bingo complete 1 gwd"
        elif tile_name not in TILES_TO_NUM.keys():
            response = "The tile options are: "
            for key in TILES_TO_NUM:
                response += f"{key}, "
            response = response[:-1]
        else:
            tile_num = TILES_TO_NUM[tile_name]
            complete_tile(self.bingo_sheet_tiles, team_num, tile_num)
            response = f"{tile_name} completed by team {team_num}.\n"

            ## HIDDEN TILES BINGO
            # tiles_left,hidden_left,hidden_tiles_left = get_number_tiles_left(self.bingo_sheet_tiles, team_num)
            # # listoftiles, number, number, list of tiles
            # if random() < hidden_left/tiles_left:
            #     new_bingo_list = [BINGO_HIDDEN[i-1] for i in hidden_tiles_left]
            #     hidden_index = randint(0,len(new_bingo_list)-1)
            #     hidden_tile = new_bingo_list[hidden_index]
            #     response += f"You rolled for the hidden tile {hidden_tile}!"
            #     tile_num2 = TILES_TO_NUM[" ".join(["hidden",str(hidden_index+1)])]
            #     reveal_tile(self.bingo_sheet_tiles, team_num,tile_num2)
        await ctx.send(response)

    @commands.command(name='undo', help='Undo a Tile.')
    @commands.has_permissions(kick_members=True)
    async def undo(self,ctx, team_num, *tile_name):
        try:
            self.bingo_sheet_tiles.col_values(1)
        except gspread.exceptions.APIError:
            self.client.login()
        tile_name = " ".join(tile_name)
        tile_name = tile_name.lower()
        team_num = int(team_num)
        if team_num not in range(1,9):
            response = "You need to specify the number of your team\n !bingo undo 1 gwd"
        elif tile_name not in TILES_TO_NUM.keys():
            response = "The tile options are: "
            for key in TILES_TO_NUM:
                response += f"{key}, "
            response = response[:-1]
        else:
            tile_num = TILES_TO_NUM[tile_name]
            undo_tile(self.bingo_sheet_tiles, team_num, tile_num)
            response = f"{tile_name} has not been done by team {team_num}."
        await ctx.send(response)

    @commands.command(name='checkdone', help='Checks tiles done by a team.')
    async def check_done(self,ctx, team_num):
        try:
            self.bingo_sheet_tiles.col_values(1)
        except gspread.exceptions.APIError:
            self.client.login()
        team_num = int(team_num)
        if team_num not in range(1,9):
            response = "You need to specify the number of your team\n !bingo checkdone 1"
            await ctx.send(response)
        else:
            _,tiles_done = get_tiles_done(self.bingo_sheet_tiles, team_num)
            if len(tiles_done)==25:
                response = f"Team {team_num} has complete the bingo, such monsters."
                await ctx.send(response)
            else:
                # response = f"Team {team_num} has finished the following tiles:\n"
                # for tile in tiles_done:
                #     response += f"{tile}\n"
                temp_img = paint_tiles(tiles_done)
                temp_img.save(f"team{team_num}.png")
                await ctx.send(file=discord.File(f"team{team_num}.png"))

    @commands.command(name='checkleft', help='Checks tiles that have not been done by a team.')
    async def check_left(self,ctx, team_num):
        try:
            self.bingo_sheet_tiles.col_values(1)
        except gspread.exceptions.APIError:
            self.client.login()
        team_num = int(team_num)
        if team_num not in range(1,9):
            response = "You need to specify the number of your team\n !bingo checkleft 1"
        else:
            tiles_left = get_tiles_left(self.bingo_sheet_tiles, team_num)
            if len(tiles_left)==0:
                response = f"Team {team_num} has complete the bingo, such monsters."
            else:
                response = f"Team {team_num} has not finished the following tiles:\n"
                for tile in tiles_left:
                    response += f"{tile}\n"
        await ctx.send(response)

    @commands.command(name='addteam', help='Add a team of players.')
    @commands.has_permissions(kick_members=True)
    async def addteam(self,ctx, team_num, *players):
        try:
            team_num = int(team_num)
            if int(team_num) not in range(1,9):
                response = "You need to specify the number of your team\n !hs addteam 1 ironrok toad_event spniz_uim thebranflake"
            else:
                team_nums = get_team_nums(self.cur)
                if team_num in team_nums:
                    response = f"Team {team_num} already exists! To check the team use !hs checkteam {team_num}"
                else:
                    add_team(self.cur,team_num, list(players))
                    response = f"Team {team_num} has been created. To check the team use !hs checkteam {team_num}"
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='getteam', help='Returns the players of a specific team. !hs checkteam 1 -> returns the players of team 1')
    async def getteam(self,ctx, team_num):
        try:
            team_num = int(team_num)
            if team_num not in range(1,9):
                response = "You need to specify the number of your team\n !hs addteam 1 ironrok toad_event spniz_uim thebranflake"
            else:
                team_nums = get_team_nums(self.cur)
                if team_num in team_nums:
                    team = get_team(self.cur,team_num)
                    response = f"Team {team_num} has the following players:\n"
                    for i,player in enumerate(team):
                        if player:
                            response += f"{i+1}. {player}\n"
                else:
                    response = f"Team {team_num} does not exist, to create it use !hs addteam {team_num} player1 player2 ... player8"
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='modifyteam', help='Updates a specific player of a team. !hs updateteam 1 5 ironrok -> updates the team 1 player 5 to ironrok.')
    @commands.has_permissions(kick_members=True)
    async def modifyteam(self,ctx, team_num, player_num, player):
        try:
            team_num = int(team_num)
            player_num = int(player_num)
            if team_num not in range(1,9):
                response = "You need to specify the number of your team\n For example team 1, player 2, name ironrok: !hs updateteam 1 2 ironrok"
            elif player_num not in range(1,9):
                response = "You need to specify the number of the player you are updating\n For example team 1, player 2, name ironrok: !hs updateteam 1 2 ironrok"
            else:
                update_team(self.cur,team_num,player_num,player)
                response = f"{player} is now player {player_num} of team {team_num}."
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='resetteams', help='Removes all teams.')
    @commands.has_permissions(kick_members=True)
    async def resetteans(self,ctx):
        try:
            reset_teams(self.cur)
            response = "Teams have been reset."
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='checkteam', help='Checks xp/kc gained by a team in a skill/boss (players with starting kc not on the highscores wont be tracked)')
    async def checkteam(self,ctx, team_num,*stat):
        team_num = int(team_num)
        try:
            if team_num not in range(1,9):
                response = "Team number must be between 1 and 8 included."
            else:
                if stat:
                    stat = ("_").join(stat).lower()
                    pretty_stat = get_stat(stat)
                    stat = coded_string(pretty_stat)
                else:
                    stat = "overall"
                    pretty_stat = "Overall"
                skill = is_skill(stat)
                if skill:
                    team_members = get_team(self.cur,team_num)
                    stat_delta = xp_gained_team(self.cur,team_num,stat,skill,team_members)
                    response = f"Team {team_num} has gained {str(stat_delta)} {pretty_stat} xp."
                else:
                    team_members = get_team(self.cur,team_num)
                    starting_kc = tracker_starting_stat_multiple(self.cur,team_members,stat,skill,'clan_tracker')
                    valid_team_members = [x[0] for x in starting_kc if int(x[1]) != -1]
                    invalid_members = [x for x in team_members if x not in valid_team_members]
                    if valid_team_members:
                        stat_delta= xp_gained_team(self.cur,team_num,stat,skill,valid_team_members)
                        response = f"Team {team_num} has done {str(stat_delta)} {pretty_stat} kills."
                        response += f"\nKc gained by {invalid_members} is not being counted because their starting kc was not in the hs."
                    else:
                        response = f"You don't have any team member being tracked in {pretty_stat} because their starting kc was not in the hs."
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='bingocommands', help='Shows all the bingo related commands')
    async def bingocommands(self,ctx):
        try:
            response = """
    !hs complete 1 raids -> completes team 1 raids tile in the sheets.
    !hs undo 1 raids -> undos team 1 raids tile in the sheets.
    !hs checkdone 1 -> shows the tiles complete by team 1 (everybody).
    !hs checkleft -> shows the tiles left of team 1 (everybody).
    !hs addteam 2 ironrok spniz_uim -> creates team number 2 and adds players ironrok and spniz_uim to it.
    !hs getteam 2 -> shows the members of team 2 (everybody).
    !hs modifyteam 2 1 cluelessprod -> cluelessprod is now player 1 of team 2.
    !hs resetteams -> removes all teams.
    !hs checkteam 1 mining -> shows xp gained by team 1 in mining (everybody).
    !hs updateteam 1 -> updates all players in team 1.
            """
        except Exception as e:
            response = str(e)
        finally:
            await ctx.send(response)

    @commands.command(name='updateteam',help='updates a bingo team on the hiscores. !hs updateteam 1')
    async def updateteam(self,ctx,team_num):
        try:
            team_num = int(team_num)
            members = get_team(self.cur,team_num)
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
                else:
                    sql_update_player_hs(self.cur,name,stats,stats_col_names)
                        # sql_add_player_hs_historic(self.self.cur,name,stats)
                        #self.conn.commit()
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


def setup(bot):
    scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    bingo_sheet_tiles = client.open("Bingo 07irons").worksheet('Tile Tracker')

    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    conn.autocommit=True
    bot.add_cog(Bingo(bot,conn,client,bingo_sheet_tiles))
    
