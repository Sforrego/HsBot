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


load_dotenv()
token1 = os.getenv('DISCORD_TOKEN1')

## SHEETS
scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
bosses_sheet = client.open("Members Ranks").worksheet('Bosses')
skills_sheet = client.open("Members Ranks").worksheet('Skills')
start_sheet = client.open("Members Ranks").worksheet('Start')
members_sheet = client.open("Members Ranks").worksheet('Members')

bingo_sheet_bosses = client.open("Lockdown Bingo").worksheet('BossTracker')
bingo_sheet_skills = client.open("Lockdown Bingo").worksheet('SkillsTracker')

#BOT

bot1 = commands.Bot(command_prefix=['!hs ','!bingo '])


@bot1.event
async def on_ready():
    print(f'{bot1.user} has connected to Discord!')
    task = loop.create_task(do_stuff_every_x_seconds(60*29, client.login))
    #task2 = loop.create_task(do_stuff_every_x_seconds(60*60*12, update_all,bosses_sheet,skills_sheet,start_sheet,client))

@bot1.command(name="updateteams",help="updates a bingo team progress. ")
@commands.has_permissions(kick_members=True)
async def update_team(ctx):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    await ctx.send("Teams updating... (this takes like 1-2 mins)")
    bingo_update(bingo_sheet_bosses,bingo_sheet_skills,skills="both")
    await ctx.send("Teams progress updated!")

@bot1.command(name="startbingo00",help="starts tracking every player participating in the bingo.")
@commands.has_permissions(kick_members=True)
async def update_team(ctx):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    await ctx.send("Starting bingo tracker... (this takes like 3-4 mins)")
    bingo_update(bingo_sheet_bosses,bingo_sheet_skills,skills="both",init=1)
    bingo_update(bingo_sheet_bosses,bingo_sheet_skills,skills="both")
    await ctx.send("Bingo tracker initialized!")

@bot1.command(name="checkteam",help="Checks a bingo team progress. \n eg: !bingo checkteam 1")
async def update_team(ctx, team):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    response = str(bingo_check(bingo_sheet_bosses,bingo_sheet_skills,team))
    response += "\n\nBoss KC might not be accurate (if you weren't ranked in the highscores in that boss when bingo began)"
    await ctx.send(response)

@bot1.command(name='add', help='Adds a player to the spreadsheets (Admin).')
@commands.has_permissions(kick_members=True)
async def add(ctx, name):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    stats = getStats(playerURL(name,'iron'))
    if stats == 404:
        response = f"{name} not found in the highscores."
    else:
        update_player(bosses_sheet,skills_sheet,start_sheet,names,name,stats,1)
        response = f"{name} has been added to the memberslist."
    await ctx.send(response)

@bot1.command(name='update', help='Updates a players stats in the spreadsheets (Admin). \n Ejemplo: !hs update ironrok Yaspy (updates both players)')
async def update(ctx, *members):
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    response = ''
    for name in members:
        stats = getStats(playerURL(name,'iron'))
        if stats == 404:
            response += f"{name} not found in the highscores.\n"
        else:
            update_player(bosses_sheet,skills_sheet,start_sheet,names,name,stats)
            response += f"{name} stats has been updated\n"
    await ctx.send(response)

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
async def change_rsn(ctx, old_name,new_name):
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    try:
        update_rsn(members_sheet,bosses_sheet,skills_sheet,start_sheet,names,old_name,new_name)
        response = f"{old_name} has been changed to {new_name} and his stats has been updated."
    except Exception as e:
        response = f"Something went wrong. Error {e}"
    await ctx.send(response)

@bot1.command(name='fullupdate', help='Updates every player (Admin).')
@commands.has_permissions(kick_members=True)
async def full_update(ctx):
    msg = f"All players are being updated ..."
    await ctx.send(msg)
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    try:
        update_all(bosses_sheet,skills_sheet,start_sheet,client)
        response = f"All players have been updated."
    except Exception:
        print(Exception)
        response = "There was an error, please try again later."
    await ctx.send(response)

@bot1.command(name='top', help='Shows the top 5 players and their kc for a specific stat.')
async def top(ctx, stat):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]

    response = get_stat_top(bosses_sheet, skills_sheet,start_sheet ,names, stat, 5)
    await ctx.send(response)

@bot1.command(name='top10', help='Shows the top X players and their kc for a specific stat.')
async def topx(ctx, stat):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    response = get_stat_top(bosses_sheet, skills_sheet,start_sheet ,names, stat, 10)
    await ctx.send(response)

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
                    await member.add_roles(role)
                    await member.edit(nick=rsn)

                    index = len(col0)+1
                    #members_cell_list = members_sheet.range(f'A{index}:B{index}')
                    members_sheet.update_acell(f"A{index}",rsn)
                    members_sheet.update_acell(f"K{index}",rsn)
                    members_sheet.update_acell(f"L{index}",rsn.replace(" ","_"))
                    members_sheet.update_acell(f"B{index}",member.joined_at.strftime("%d %b, %Y"))
                    names.append(rsn.replace(" ","_").lower())
                    update_player(bosses_sheet,skills_sheet,start_sheet,names,rsn.replace(" ","_"),stats)
                    response = f"{rsn} has been added to the memberlist, given nickname and role, and updated in the clan's HS."
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

    for name in members:
        if name.lower() not in names:
            not_found.append(name)
        else:

            index = names.index(name.lower())+2
            names.remove(name.lower())
            start_sheet.delete_row(index)
            bosses_sheet.delete_row(index)
            members_sheet.delete_row(index)
            skills_sheet.delete_row(index)

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
async def get_boss_list(ctx, *args):
    rsn = "_".join(args)
    rsn2 = " ".join(args)
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    if check(names,rsn):
        response = f"{rsn2} is in the highscores."
    else:
        response = f"{rsn2} is not in the highscores."
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

bot2 = commands.Bot(command_prefix=['!corner ','!notify '])

@bot2.event
async def on_ready():
    print(f'{bot2.user} has connected to Discord!')


@bot2.command(name='send', help='Assigns corner role to member for duration minutes')
@commands.has_permissions(kick_members=True)
async def restrict(ctx, member:discord.Member, duration: int):
    role = discord.utils.get(ctx.guild.roles, name="Corner")
    await member.add_roles(role)
    name = member.nick if member.nick else member.name
    response = f"{name} has been sent to the corner for {duration} minutes."
    await ctx.send(response)
    await asyncio.sleep(duration*60)
    await member.remove_roles(role)


@bot2.command(name='remove',help ='Removes Corner role from a specific member.')
@commands.has_permissions(kick_members=True)
async def remove_corners(ctx, member:discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Corner")
    await member.remove_roles(role)

@bot2.command(name='reset', help ='Removes Corner role from every member.')
@commands.has_permissions(kick_members=True)
async def remove_corners(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Corner")
    for member in ctx.guild.members:
        await member.remove_roles(role)

@bot2.command(name='members')
@commands.has_permissions(kick_members=True)
async def remove_corners(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Corner")
    members_in_corner = ''
    for member in ctx.guild.members:
        if role in member.roles:
            name = member.nick if member.nick else member.name
            members_in_corner += f'{name}\n'
    if members_in_corner == '':
        members_in_corner = 'No members in the corner.'
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
