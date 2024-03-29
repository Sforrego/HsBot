import os
import gspread
import discord
from discord.ext import commands
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
import time
import httplib2
from discord.ext.commands import MemberConverter
## make one function that creates an object after calling rs.hs make the other funcs receive that.
from random import randint,random
from constants import RANKS, RANKS2, boss_shorts
from funcs import update_rsn,get_stat
import psycopg2
from getstats import getStats,playerURL
load_dotenv()



### DB ####

# live mode

token1 = os.getenv('DISCORD_TOKEN1')
# remember loop bot2
bot1 = commands.Bot(command_prefix=['!hs '])

# # test mode
# # comment bot 2
# user = os.getenv('user')
# password = os.getenv('password')
# host = os.getenv('host')
# port = os.getenv('port')
# database = os.getenv('database')
# conn = psycopg2.connect(user=user,password=password,host=host,port=port,database=database)
#
# token1 = os.getenv('TEST_TOKEN')
# bot1 = commands.Bot(command_prefix=['!test '])
# # end test mode ###

bot1.load_extension('hs_cog')
bot1.load_extension('tracker_cog')
bot1.load_extension('bingo_cog')



## SHEETS
scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

members_sheet = client.open("Members Ranks").worksheet('Members')


# bingo_sheet_bosses = client.open("Bingo 07irons").worksheet('BossTracker')
# bingo_sheet_skills = client.open("Bingo 07irons").worksheet('SkillsTracker')
bingo_sheet_tiles = client.open("Bingo 07irons").worksheet('Tile Tracker')


### connecting to database ###
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit=True
cur = conn.cursor()

#BOT 1



#await channel.send(file=discord.File('my_file.png'))

@bot1.event
async def on_ready():
    print(f'{bot1.user} has connected to Discord!')
    loop.create_task(do_stuff_every_x_seconds(60*29, client.login))
    #task2 = loop.create_task(do_stuff_every_x_seconds(60*60*24, update_all,bosses_sheet,skills_sheet,start_sheet,client))




#### NEW HS DB COMMANDS #####




##### END OF DB HS COMMANDS ######




@bot1.command(name='change', help='Changes a players rsn in the spreadsheets (Admin).')
@commands.has_permissions(kick_members=True)
async def change_rsn(ctx, member,*new_name):
    converter = MemberConverter()
    new_name = " ".join(new_name)
    try:
        names = members_sheet.col_values(11)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = members_sheet.col_values(11)[1:]
    try:
        member = await converter.convert(ctx,member)
        if member.nick:
            old_name = member.nick
        else:
            old_name = member.name
        ol_name = old_name.replace(" ", "_")
        update_rsn(members_sheet,names,ol_name,new_name)
        await member.edit(nick=new_name)
        response = f"{old_name} has been changed to {new_name}."
    except Exception as e:
        response = f"Something went wrong. Error {e}"
    await ctx.send(response)

#### CLAN MEMBERS STUFF ##### 

@bot1.command(name='clan_ranks', help='Return all players with a specific rank (Admin).')
@commands.has_permissions(kick_members=True)
async def ranks(ctx, *rank):
    rank = " ".join(rank)
    try:
        names = members_sheet.col_values(11)[1:]
    except gspread.exceptions.APIError:
        client.login()
        names = members_sheet.col_values(11)[1:]
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
        names = members_sheet.col_values(11)[1:]
    except gspread.exceptions.APIError:
        client.login()
        names = members_sheet.col_values(11)[1:]
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

# @bot1.command(name='compare', help='Compares two players in a specific stat.')
# async def compare(ctx, stat, player1, player2):
#     try:
#         names = members_sheet.col_values(11)[1:]
#     except gspread.exceptions.APIError as e:
#         client.login()
#         names = members_sheet.col_values(11)[1:]
#     p1,p2 = player1.lower(), player2.lower()
#     stat = get_stat(stat)
#     if not stat:
#         response = f"Stat not found."
#         await ctx.send(response)
#         return
#     print(f"{stat}")
#     if p1 not in names:
#         response = f"Player {p1} not found."
#         await ctx.send(response)
#         return
#     if p2 not in names:
#         response = f"Player {p2} not found."
#         await ctx.send(response)
#         return
#     comparison = compare_players(bosses_sheet, skills_sheet, names, p1, p2, stat)
#     winner = comparison[0]
#     player1,player2 = get_pretty_names(members_sheet,[p1,p2])
#     response = f"{stat} \n"
#     if len(comparison) == 5: #this is a skill
#         if winner:
#             response += f"1. {player1} {comparison[2]} {comparison[1]} \n"
#             response += f"2. {player2} {comparison[4]} {comparison[3]} "
#         else:
#             response += f"1. {player2} {comparison[4]} {comparison[3]} \n"
#             response += f"2. {player1} {comparison[2]} {comparison[1]} "
#     elif len(comparison) == 3:
#         if winner:
#             response += f"1. {player1} {comparison[1]}\n"
#             response += f"2. {player2} {comparison[2]}"
#         else:
#             response += f"1. {player2} {comparison[2]}\n"
#             response += f"2. {player1} {comparison[1]}"
#     await ctx.send(response)

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
                    names = members_sheet.col_values(11)[1:]
                except gspread.exceptions.APIError as e:
                    client.login()
                    names = members_sheet.col_values(11)[1:]
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
                    members_sheet.update_acell(f"J{index}",rsn)
                    members_sheet.update_acell(f"B{index}",member.joined_at.strftime("%d %b, %Y"))
                    members_sheet.update_acell(f"L{index}",member.name)
                    response = f"{rsn} has been added to the memberlist, given nickname and role, and added in the clan's HS."
    except discord.ext.commands.errors.BadArgument:
        response = f"Member {member} not found."
    except Exception as e:
        response = str(e)
    finally:
        await ctx.send(response)



@bot1.command(name='joindate', help='Shows a player and their join date.')
@commands.has_permissions(kick_members=True)
async def joindate(ctx,*member):
    member = " ".join(member)
    converter = MemberConverter()
    member = await converter.convert(ctx,member)
    print(f"Member name: {member.name}. Nickname: {member.nick}")
    response = f"{str(member)} {member.nick} Joined: {member.joined_at}.\n"
    await ctx.send(response)

@bot1.command(name='myjoindate', help='Shows your join date.')
async def myjoindate(ctx):
    member = ctx.message.author.display_name
    converter = MemberConverter()
    member = await converter.convert(ctx,member)
    print(f"Member name: {member.name}. Nickname: {member.nick}")
    response = f"{str(member)} {member.nick} Joined: {member.joined_at}.\n"
    await ctx.send(response)

@bot1.command(name='remove', help='Removes players from the cc (sheets) (Admin) (Replace spaces in names with underscore)\n Example: !hs remove Ironrok b_Ee_Z.')
@commands.has_permissions(kick_members=True)
async def memberslit(ctx,*members):
    try:
        names = members_sheet.col_values(11)[1:]
    except gspread.exceptions.APIError:
        client.login()
        names = members_sheet.col_values(11)[1:]
    not_found = []
    await ctx.send("Deleting")
    for name in members:
        if name.lower() not in names:
            not_found.append(name)
        else:
            index = names.index(name.lower())+2
            names.remove(name.lower())
            members_sheet.delete_row(index)
            print(f"{name} deleted")
    found = [x for x in members if x not in not_found]
    response = f'Deleted \n{found}\n \nNot Found \n {not_found}'

    await ctx.send(response)


# @bot1.command(name='bossestop', help='Prints the top 5 players for every boss (Admin).')
# @commands.has_permissions(kick_members=True)
# async def full_bosses_print(ctx):
#     pass

@bot1.command(name='shorts', help='Gets all the short ways of calling each stat (Case insensitive and spaces must be replaced with _).')
async def get_boss_list(ctx):
    response = str(list(boss_shorts.keys()))
    response += "\nIf the name is not on the list use the correct stat name\n"
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

bot2 = commands.Bot(command_prefix=['!command '])

@bot2.event
async def on_ready2():
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
async def remove_corners_all(ctx):
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
async def notify_all(ctx):
    role = discord.utils.get(ctx.guild.roles, name="NotifyOn")
    for member in ctx.guild.members:
        await member.add_roles(role)
    await ctx.send("Everyone will be notified.")
@bot2.command(name='none')
async def dont_notify_all(ctx):
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
