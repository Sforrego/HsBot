import os
import gspread
import discord
from discord.ext import commands
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from funcs import *
import asyncio

load_dotenv()
token1 = os.getenv('DISCORD_TOKEN1')

## SHEETS
scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
bosses_sheet = client.open("07 Irons HiScore").get_worksheet(0)
skills_sheet = client.open("07 Irons HiScore").get_worksheet(1)
start_sheet = client.open("07 Irons HiScore").get_worksheet(2)


#BOT

bot1 = commands.Bot(command_prefix='!hs ')

@bot1.event
async def on_ready():
    print(f'{bot1.user} has connected to Discord!')



@bot1.command(name='add', help='Adds a player to the spreadsheets (Admin).')
@commands.has_permissions(kick_members=True)
async def add(ctx, name):
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    update_player(bosses_sheet,skills_sheet,start_sheet,names,name,1)
    response = f"{name} has been added to the memberslist."
    await ctx.send(response)

@bot1.command(name='update', help='Updates a players stats in the spreadsheets (Admin).')
@commands.has_permissions(kick_members=True)
async def update(ctx, name):
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    update_player(bosses_sheet,skills_sheet,start_sheet,names,name,0)
    response = f"{name} stats has been updated."
    await ctx.send(response)

@bot1.command(name='change', help='Changes a players rsn in the spreadsheets (Admin).')
@commands.has_permissions(kick_members=True)
async def change_rsn(ctx, old_name,new_name):
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    update_rsn(bosses_sheet,skills_sheet,start_sheet,names,old_name,new_name)
    response = f"{old_name} has been changed to {new_name} and his stats has been updated."
    await ctx.send(response)

@bot1.command(name='fullupdate', help='Updates every player (Admin).')
@commands.has_permissions(kick_members=True)
async def full_update(ctx):
    msg = f"All players are being updated ..."
    await ctx.send(msg)
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    update_all(bosses_sheet,skills_sheet,names)
    response = f"All players have been updated."
    await ctx.send(response)

@bot1.command(name='top', help='Shows the top 5 players and their kc for a specific stat.')
async def top(ctx, stat):
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    response = get_stat_top(bosses_sheet, skills_sheet,start_sheet ,names, stat, 5)
    await ctx.send(response)

@bot1.command(name='topx', help='Shows the top X players and their kc for a specific stat.')
async def top(ctx, stat, n):
    if int(n) <= 10:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
        response = get_stat_top(bosses_sheet, skills_sheet,start_sheet ,names, stat, int(n))
    else:
        response = "N has to be 10 or lower."
    await ctx.send(response)


@bot1.command(name='compare', help='Compares two players in a specific stat.')
async def compare(ctx, stat, player1, player2):
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]
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
            response += f"2. {player2} {comparison[4]} {comparison[3]} \n"
            response += f"1. {player1} {comparison[2]} {comparison[1]} "
    elif len(comparison) == 3:
        if winner:
            response += f"1. {player1} {comparison[1]}\n"
            response += f"2. {player2} {comparison[2]}"
        else:
            response += f"2. {player2} {comparison[2]}\n"
            response += f"1. {player1} {comparison[1]}"
    await ctx.send(response)

@bot1.command(name='bossestop', help='Prints the top 5 players for every boss (Admin).')
@commands.has_permissions(kick_members=True)
async def full_bosses_print(ctx):
    pass

##########################################################
##################### bot 2 ##############################
##########################################################
token2 = os.getenv('DISCORD_TOKEN2')

bot2 = commands.Bot(command_prefix='!corner ')

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




loop = asyncio.get_event_loop()
loop.create_task(bot1.start(token1))
loop.create_task(bot2.start(token2))
loop.run_forever()

# bot1.run(token1)
#
#
# bot2.run(token2)