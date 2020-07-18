import os
import gspread
import discord
from discord.ext import commands
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from funcs import *
import asyncio
import time
import httplib2
from discord.ext.commands import MemberConverter
## make one function that creates an object after calling rs.hs make the other funcs receive that.
from random import randint
from imageediting import *
from sqlfuncs import *

import psycopg2
load_dotenv()

### DB ####
DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


## SHEETS
scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
bosses_sheet = client.open("Members Ranks").worksheet('Bosses')
skills_sheet = client.open("Members Ranks").worksheet('Skills')
start_sheet = client.open("Members Ranks").worksheet('Start')
members_sheet = client.open("Members Ranks").worksheet('Members')
tracker_sheet = client.open("Members Ranks").worksheet('WeeklyTracker')
tracked_sheet = client.open("Members Ranks").worksheet('TrackedXp')

# bingo_sheet_bosses = client.open("Bingo 07irons").worksheet('BossTracker')
# bingo_sheet_skills = client.open("Bingo 07irons").worksheet('SkillsTracker')
bingo_sheet_tiles = client.open("Bingo 07irons").worksheet('Tile Tracker')

#BOT 1
token1 = os.getenv('DISCORD_TOKEN1')

bot1 = commands.Bot(command_prefix=['!hs ','!bingo '])

#await channel.send(file=discord.File('my_file.png'))

@bot1.event
async def on_ready():
    print(f'{bot1.user} has connected to Discord!')
    #task = loop.create_task(do_stuff_every_x_seconds(60*29, client.login))
    #task2 = loop.create_task(do_stuff_every_x_seconds(60*60*24, update_all,bosses_sheet,skills_sheet,start_sheet,client))

#### BINGO ####
@bot1.command(name='roll', help='Rolls randomly from the board or the list.')
@commands.has_permissions(kick_members=True)
async def roll(ctx, type):
    if type == "board":
        response = BINGO_TILES[randint(0,len(BINGO_TILES)-1)]
    elif type == "list":
        response = BINGO_LIST[randint(0,len(BINGO_LIST)-1)]
    else:
        response = "You can either do !hs roll board or !hs roll list."
    await ctx.send(response)

@bot1.command(name='complete', help='Completes a Tile.')
@commands.has_permissions(kick_members=True)
async def complete(ctx, team_num, *tile_name):
    try:
        names = start_sheet.col_values(2)
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)
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
        complete_tile(bingo_sheet_tiles, team_num, tile_num)
        response = f"{tile_name} completed by team {team_num}."
    await ctx.send(response)
@bot1.command(name='undo', help='Undo a Tile.')
@commands.has_permissions(kick_members=True)
async def undo(ctx, team_num, *tile_name):
    try:
        names = start_sheet.col_values(2)
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)
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
        undo_tile(bingo_sheet_tiles, team_num, tile_num)
        response = f"{tile_name} has not been done by team {team_num}."
    await ctx.send(response)

@bot1.command(name='checkdone', help='Checks tiles done by a team.')
async def check_done(ctx, team_num):
    try:
        names = start_sheet.col_values(2)
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)
    team_num = int(team_num)
    if team_num not in range(1,9):
        response = "You need to specify the number of your team\n !bingo checkdone 1"
        await ctx.send(response)
    else:
        _,tiles_done = get_tiles_done(bingo_sheet_tiles, team_num)
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

@bot1.command(name='checkleft', help='Checks tiles that have not been done by a team.')
async def check_left(ctx, team_num):
    try:
        names = start_sheet.col_values(2)
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)
    team_num = int(team_num)
    if team_num not in range(1,9):
        response = "You need to specify the number of your team\n !bingo checkleft 1"
    else:
        tiles_left = get_tiles_left(bingo_sheet_tiles, team_num)
        if len(tiles_left)==0:
            response = f"Team {team_num} has complete the bingo, such monsters."
        else:
            response = f"Team {team_num} has not finished the following tiles:\n"
            for tile in tiles_left:
                response += f"{tile}\n"
    await ctx.send(response)



#### END BINGO ####


#### NEW HS DB COMMANDS #####


@bot1.command(name='update', help="Updates a players stats in the clan's hiscores. \n eg: !hs update ironrok r_a_df_o_r_d (updates both players you can do as many as you want)")
async def update_hs(ctx, *members):
    first_msg = 'Updating '
    for member in members:
        first_msg += f'{member} '
    await ctx.send(first_msg)
    not_found_osrs = []
    not_found_cc = []
    for name in members:
        stats = getStats(playerURL(name,'iron'))
        if stats == 404:
            not_found_osrs.append(name)
        else:
            try:
                sql_update_player_hs(cur,name,stats_col_names,stats)
                sql_add_player_hs_historic(cur,name,stats)
            except Exception as e:
                not_found_cc.append(name)
    conn.commit()
    found = [x for x in members if (x not in not_found_cc and x not in not_found_osrs)]
    response = f"{found} has been updated!"
    if not_found_osrs:
        response+= f"{not_found_osrs} were not found in the osrs' hiscores.\n"
    if not_found_cc:
        response+= f"{not_found_cc} were not found on the clan's hiscores.\n"
    await ctx.send(response)

@bot1.command(name='add', help="Adds players to the clan's hiscores. \n eg: !hs addhs ironrok r_a_df_o_r_d (updates both players you can do as many as you want)")
@commands.has_permissions(kick_members=True)
async def add_hs(ctx, *members):
    first_msg = 'Adding '
    for member in members:
        first_msg += f'{member} '
    first_msg += "to the clan's hs."
    await ctx.send(first_msg)
    not_found_osrs = []
    not_found_cc = []
    for name in members:
        stats = getStats(playerURL(name,'iron'))
        if stats == 404:
            not_found_osrs.append(name)
        else:
            try:
                sql_add_player_hs(cur,name,stats)
                sql_add_player_hs_historic(cur,name,stats)
            except Exception as e:
                not_found_cc.append(name)
    conn.commit()
    found = [x for x in members if (x not in not_found_cc and x not in not_found_osrs)]
    response = f"{found} has been added!"
    if not_found_osrs:
        response+= f"{not_found_osrs} were not found in the osrs' hiscores.\n"
    if not_found_cc:
        response+= f"{not_found_cc} something went wrong adding these players.\n"
    await ctx.send(response)


@bot1.command(name='top', help="Shows the top 5 players and their kc/lvl+xp for a specific stat.")
async def top_hs(ctx, stat):
    response = ""
    stat = get_stat(stat).lower()
    try:
        skill = is_skill(stat)
        result = sql_top_stat(cur,stat,5,skill,stats_col_names)
        response = top_stat_to_string(result)
    except Exception as e:
        response = e
    finally:
        print(response)
        await ctx.send(response)

@bot1.command(name='top10', help="Shows the top 10 players and their kc/lvl+xp for a specific stat.")
async def top_hs(ctx, stat):
    response = ""
    stat = get_stat(stat).lower()
    try:
        skill = is_skill(stat)
        result = sql_top_stat(cur,stat,10,skill,stats_col_names)
        response = top_stat_to_string(result)
    except Exception as e:
        response = e
    finally:
        print(response)
        await ctx.send(response)


@bot1.command(name='checkhs', help="Checks if a player is in the clan´s hs.")
async def check_hs(ctx, name):
    players = get_players_in_hs(cur)
    if name in players:
        response = f"{name} is in the clan´s hiscores."
    else:
        response = f"{name} is not in the clan´s hiscores."

    await ctx.send(response)

@bot1.command(name='my', help="Gets the person using the command lvl/kc in a stat.")
async def check_hs(ctx, stat):
    name = coded_string(ctx.message.author.nick)
    stat = get_stat(stat).lower()
    try:
        skill = is_skill(stat)
        result = get_player_stat(cur,name,stat,skill,stats_col_names)[0]
        if skill:
            response = f"{name}'s {stat} level: {result[1]} with {reult[2]} xp."
        else:
            response = f"{name}'s {stat} kc: {result[1]}."

    except Exception as e:
        response = e
    finally:
        await ctx.send(response)

@bot1.command(name='fullupdate', help="Updates every player in the clan's hiscores.")
async def fullupdate(ctx):
    await ctx.send("Updating all players...")
    members = get_players_in_hs(cur)
    not_found_osrs = []
    for name in members:
        stats = getStats(playerURL(name,'iron'))
        if stats == 404:
            not_found_osrs.append(name)
        else:
            try:
                sql_update_player_hs(cur,name,stats_col_names,stats)
                sql_add_player_hs_historic(cur,name,stats)
            except Exception as e:
                not_found_cc.append(name)
    conn.commit()

    if not_found_osrs:
        response+= f"{not_found_osrs} were not found in the osrs' hiscores.\n"
        await ctx.send(response)

    await ctx.send("Finished updating.")

##### END OF DB HS COMMANDS ######

@bot1.command(name='ranks', help='Shows the rank within the clan of a member in all the skills. (!hs ranks bosses player or !hs ranks skills player)')
async def ranks(ctx,stat,name):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]

    stat = 1 if stat == "bosses" else 0
    answer_dict = player_top_stats(bosses_sheet, skills_sheet, start_sheet, names, name, stat)
    [name] = get_pretty_names(start_sheet,[name.lower()])
    response = f"\n{name}\n\n"
    for key in answer_dict:
        response += f"{key}: {answer_dict[key]}\n"
    await ctx.send(response)


@bot1.command(name='change', help='Changes a players rsn in the spreadsheets (Admin).')
@commands.has_permissions(kick_members=True)
async def change_rsn(ctx, member,*new_name):
    converter = MemberConverter()
    new_name = " ".join(new_name)
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    try:
        member = await converter.convert(ctx,member)
        if member.nick:
            old_name = member.nick
        else:
            old_name = member.name
        ol_name = old_name.replace(" ", "_")
        update_rsn(members_sheet,bosses_sheet,skills_sheet,start_sheet,names,ol_name,new_name)
        await member.edit(nick=new_name)
        response = f"{old_name} has been changed to {new_name}."
    except Exception as e:
        response = f"Something went wrong. Error {e}"
    await ctx.send(response)

####### TRACKER #######

@bot1.command(name='tracked', help='Shows the top 5 players and their xp gains for a specific skill.')
async def top_track(ctx, stat,*player):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    await ctx.send("Fetching Data...")
    with open('tracking.txt','r') as file:
        tracked_players = [x.strip() for x in file.readlines()]
    if not player:
        response = get_tracked_top(tracked_sheet,start_sheet ,names, stat, 10,tracked_players)
    else:
        orig_name = " ".join(player)
        player = "_".join(player)
        player = player.lower()
        if player in names:
            (xp,player) = tracked_player(tracked_sheet,names, stat, player)
            response = f"{orig_name} has gained {xp} in {stat} this week."
        else:
            response = f"{orig_name} not found."
    await ctx.send(response)

@bot1.command(name='tracked20', help='Shows the top 20 players and their xp gains for a specific skill.')
async def top_track20(ctx, stat):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    await ctx.send("Fetching data...")
    with open('tracking.txt','r') as file:
        tracked_players = [x.strip() for x in file.readlines()]
    response = get_tracked_top(tracked_sheet,start_sheet ,names, stat, 20,tracked_players)

    await ctx.send(response)




@bot1.command(name='track', help='Adds players to the tracker.')
@commands.has_permissions(kick_members=True)
async def track(ctx,*names):
    print("Start tracking")
    await ctx.send("Fetching Started...")
    try:
        fix = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        fix = [x.lower() for x in start_sheet.col_values(2)[1:]]
    try:
        not_founds = []

        with open('tracking.txt','r') as file:
            tracked_players = [x.strip() for x in file.readlines()]

        with open('tracking.txt','a') as file:
            for name in names:
                if name not in tracked_players:
                    stats = getStats(playerURL(name,'iron'))
                    if stats == 404:
                        not_founds.append(name)
                    else:
                        update_player(bosses_sheet,skills_sheet,start_sheet,fix,name,stats,tracker_sheet=tracker_sheet)
                        name = name.lower()
                        file.write(f"{name}\n")
                        tracked_players.append(name)
        await ctx.send(f"{not_founds} Not Found in hs.\n The rest of the players are being tracked.")
    except Exception as e:
        response = f"Something went wrong. Error {e}"
        await ctx.send(response)

@bot1.command(name='updatetracker', help='Updates all the players that are being tracked(skills).')
async def update_tracker(ctx):
    print("Updating tracking")
    await ctx.send("Updating tracker...")
    with open('tracking.txt','r') as file:
        tracked_players = [x.strip() for x in file.readlines()]
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    for name in tracked_players:
        stats = getStats(playerURL(name,'iron'))
        if stats == 404:
            not_founds.append(name)
        else:
            update_player(bosses_sheet,skills_sheet,start_sheet,names,name,stats)
    await ctx.send("Tracker updated!")

@bot1.command(name='checktracker', help='Checks all the players that are being tracked(skills).')
async def check_tracker(ctx):
    with open('tracking.txt','r') as file:
        tracked_players = [x.strip() for x in file.readlines()]
    await ctx.send(f"Players being tracked: {tracked_players}.")

@bot1.command(name='resettracker', help='Reset all the players that are being tracked(skills).')
@commands.has_permissions(kick_members=True)
async def reset_tracker(ctx):
    with open('tracking.txt','r+') as file:
        file.truncate(0)
    await ctx.send(f"There are no players being tracked.")



####### END TRACKER ######

@bot1.command(name='clan_ranks', help='Return all players with a specific rank (Admin).')
@commands.has_permissions(kick_members=True)
async def ranks(ctx, *rank):
    rank = " ".join(rank)
    try:
        names = start_sheet.col_values(1)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(1)[1:]
    if rank in RANKS.keys():
        members_has_rank = []
        rank1 = members_sheet.col_values(RANKS[rank])
        rank2 = members_sheet.col_values(RANKS[rank]+1)
        for i,value in enumerate(rank1,start=0):
            if value == "GIVEN" and rank2[i]!="GIVEN":
                members_has_rank.append(names[i-1])
    response = f"{RANKS2[RANKS[rank]]}\n{members_has_rank}"
    await ctx.send(response[:1998])

@bot1.command(name='due', help='Return all players due rank in the spreadsheets (Admin).')
@commands.has_permissions(kick_members=True)
async def due(ctx,rank):
    try:
        names = start_sheet.col_values(1)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(1)[1:]
    members_due_rank = []
    if rank == "all":
        members_values = members_sheet.get_all_values()[1:]
        for i,value in enumerate(members_values,start=2):
            if "TRUE" in value:
                members_due_rank.append(value[0])
        response = f"{members_due_rank}"
    else:
        if rank in RANKS.keys():
            rank1 = members_sheet.col_values(RANKS[rank])
            for i,value in enumerate(rank1,start=0):
                if value == "TRUE":

                    members_due_rank.append(names[i-1])
            response = f"Due for {RANKS2[RANKS[rank]]}\n {members_due_rank}"
        else:
            response = f"That option is not valid, choose from: all, {RANKS.keys}"
    await ctx.send(response[:1998])

@bot1.command(name='compare', help='Compares two players in a specific stat.')
async def compare(ctx, stat, player1, player2):
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    p1,p2 = player1.lower(), player2.lower()
    stat = get_stat(stat)
    if not stat:
        response = f"Stat not found."
        await ctx.send(response)
        return
    print(f"{stat}")
    if p1 not in names:
        response = f"Player {p1} not found."
        await ctx.send(response)
        return
    if p2 not in names:
        response = f"Player {p2} not found."
        await ctx.send(response)
        return
    comparison = compare_players(bosses_sheet, skills_sheet, names, p1, p2, stat)
    winner = comparison[0]
    player1,player2 = get_pretty_names(start_sheet,[p1,p2])
    response = f"{stat} \n"
    if len(comparison) == 5: #this is a skill
        if winner:
            response += f"1. {player1} {comparison[2]} {comparison[1]} \n"
            response += f"2. {player2} {comparison[4]} {comparison[3]} "
        else:
            response += f"1. {player2} {comparison[4]} {comparison[3]} \n"
            response += f"2. {player1} {comparison[2]} {comparison[1]} "
    elif len(comparison) == 3:
        if winner:
            response += f"1. {player1} {comparison[1]}\n"
            response += f"2. {player2} {comparison[2]}"
        else:
            response += f"1. {player2} {comparison[2]}\n"
            response += f"2. {player1} {comparison[1]}"
    await ctx.send(response)

@bot1.command(name='superadd', help='Changes a players discord nick, gives him role, and adds him to ml (Admin).')
@commands.has_permissions(kick_members=True)
async def superadd(ctx, member,*args):
    #check spreadsheet if member is already there.
    converter = MemberConverter()
    try:
        member = await converter.convert(ctx,member)
        if "Member" in [x.name for x in member.roles]:
            response = f"{member} already has Member rank."
        else:
            rsn = " ".join(args)
            stats = getStats(playerURL(rsn,'iron'))
            if stats == 404:
                response = f"{rsn} not found in the highscores."
            else:
                try:
                    names = start_sheet.col_values(2)[1:]
                except gspread.exceptions.APIError as e:
                    client.login()
                    names = start_sheet.col_values(2)[1:]
                col0 = members_sheet.col_values(1)
                if rsn.replace(" ","_").lower() in names:
                    response = f"{rsn} is already in the memberlist (spreadsheet)."
                else:
                    role = discord.utils.get(ctx.guild.roles, name="Member")
                    role2 = discord.utils.get(ctx.guild.roles, name="NotifyOn")
                    await member.add_roles(role)
                    await member.add_roles(role2)

                    await member.edit(nick=rsn)

                    index = len(col0)+1
                    #members_cell_list = members_sheet.range(f'A{index}:B{index}')
                    members_sheet.update_acell(f"A{index}",rsn)
                    members_sheet.update_acell(f"K{index}",rsn)
                    members_sheet.update_acell(f"B{index}",member.joined_at.strftime("%d %b, %Y"))
                    members_sheet.update_acell(f"M{index}",member.name)
                    response = f"{rsn} has been added to the memberlist, given nickname and role, and added in the clan's HS."
    except discord.ext.commands.errors.BadArgument:
        response = f"Member {member} not found."
    except Exception as e:
        response = str(e)
    finally:
        await ctx.send(response)



@bot1.command(name='joindate', help='Shows a player and their join date.')
@commands.has_permissions(kick_members=True)
async def memberslit(ctx,*member):
    member = " ".join(member)
    converter = MemberConverter()
    member = await converter.convert(ctx,member)
    print(f"Member name: {member.name}. Nickname: {member.nick}")
    response = f"{str(member)} {member.nick} Joined: {member.joined_at}.\n"
    await ctx.send(response)

@bot1.command(name='remove', help='Removes players from the cc (sheets) (Admin) (Replace spaces in names with underscore)\n Example: !hs remove Ironrok b_Ee_Z.')
@commands.has_permissions(kick_members=True)
async def memberslit(ctx,*members):
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    not_found = []
    await ctx.send("Deleting")
    for name in members:
        if name.lower() not in names:
            not_found.append(name)
        else:

            index = names.index(name.lower())+2
            names.remove(name.lower())
            tracker_sheet.delete_row(index)
            tracked_sheet.delete_row(index)
            start_sheet.delete_row(index)
            bosses_sheet.delete_row(index)
            members_sheet.delete_row(index)
            skills_sheet.delete_row(index)
            print(f"{name} deleted")
    found = [x for x in members if x not in not_found]
    response = f'Deleted \n{found}\n \nNot Found \n {not_found}'

    await ctx.send(response)


# @bot1.command(name='bossestop', help='Prints the top 5 players for every boss (Admin).')
# @commands.has_permissions(kick_members=True)
# async def full_bosses_print(ctx):
#     pass

@bot1.command(name='list', help='Gets all the short ways of calling each stat (Case insensitive and spaces must be replaced with _).')
async def get_boss_list(ctx):
    response = str(get_stats_shorts())
    response += "\nIf the name is not on the list use the regular name (change spaces with _)\n"
    await ctx.send(response)

@bot1.command(name='check', help='Checks if a name is in the hiscores.')
async def check1(ctx, *args):
    rsn = "_".join(args)
    rsn2 = " ".join(args)
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    if check(names,rsn):
        response = f"{rsn2} is in the clan's highscores."
    else:
        response = f"{rsn2} is not in the clan's highscores."
    await ctx.send(response)






async def do_stuff_every_x_seconds(timeout, stuff, *args):
    start = time.time()
    while True:

        await asyncio.sleep(timeout)
        print(time.time()-start)
        stuff(*args)




##########################################################
##################### bot 2 ##############################
##########################################################
token2 = os.getenv('DISCORD_TOKEN2')

bot2 = commands.Bot(command_prefix=['!command ','!notify '])

@bot2.event
async def on_ready():
    print(f'{bot2.user} has connected to Discord!')

#Courtroom

@bot2.command(name='send', help='Assigns corner/court role to member for duration minutes')
@commands.has_permissions(kick_members=True)
async def restrict(ctx, role, member:discord.Member, duration=60):
    duration = int(duration)
    if role == "corner":
        role = discord.utils.get(ctx.guild.roles, name="Corner")
        await member.add_roles(role)
        name = member.nick if member.nick else member.name
        response = f"{name} has been sent to the corner for {duration} minutes."
        await ctx.send(response)
        await asyncio.sleep(duration*60)
        await member.remove_roles(role)
    if role == "court":
        role = discord.utils.get(ctx.guild.roles, name="Courtroom")
        await member.add_roles(role)
        name = member.nick if member.nick else member.name
        response = f"{name} has been sent to the court for {duration} minutes."
        await ctx.send(response)
        await asyncio.sleep(duration*60)
        await member.remove_roles(role)


@bot2.command(name='remove',help ='Removes corner/court role from a specific member.')
@commands.has_permissions(kick_members=True)
async def remove_corners(ctx, role, member:discord.Member):
    if role == "corner":
        role = discord.utils.get(ctx.guild.roles, name="Corner")
    elif role =="court":
        role = discord.utils.get(ctx.guild.roles, name="Courtroom")
    await member.remove_roles(role)

@bot2.command(name='reset', help ='Removes Corner role from every member.')
@commands.has_permissions(kick_members=True)
async def remove_corners(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Corner")
    for member in ctx.guild.members:
        await member.remove_roles(role)

@bot2.command(name='members', help= "Shows all the members with a role. eg: !command members Corner.")
@commands.has_permissions(kick_members=True)
async def members(ctx,role):

    role = discord.utils.get(ctx.guild.roles, name=role)
    members_in_corner = ''
    for member in ctx.guild.members:
        if role in member.roles:
            name = member.nick if member.nick else member.name
            members_in_corner += f'{name}\n'
    if members_in_corner == '':
        members_in_corner = f'No members with role {role}.'
    await ctx.send(members_in_corner)

@bot2.command(name='on')
async def notify_me(ctx):
    role = discord.utils.get(ctx.guild.roles, name="NotifyOn")
    await ctx.message.author.add_roles(role)
    await ctx.send("You will be notified.")

@bot2.command(name='off')
async def dont_notify_me(ctx):
    role = discord.utils.get(ctx.guild.roles, name="NotifyOn")
    await ctx.message.author.remove_roles(role)
    await ctx.send("You will not be notified.")

@bot2.command(name='all')
async def dont_notify_me(ctx):
    role = discord.utils.get(ctx.guild.roles, name="NotifyOn")
    for member in ctx.guild.members:
        await member.add_roles(role)
    await ctx.send("Everyone will be notified.")
@bot2.command(name='none')
async def dont_notify_me(ctx):
    role = discord.utils.get(ctx.guild.roles, name="NotifyOn")
    for member in ctx.guild.members:
        await member.remove_roles(role)
    await ctx.send("Everyone will not be notified.")




loop = asyncio.get_event_loop()
loop.create_task(bot1.start(token1))
loop.create_task(bot2.start(token2))

loop.run_forever()



# bot1.run(token1)
#
#
# bot2.run(token2)
