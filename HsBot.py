import os
import gspread
import discord
from discord.ext import commands
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from funcs import *
import asyncio

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

## SHEETS
scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
bosses_sheet = client.open("07 Irons HiScore").get_worksheet(0)
skills_sheet = client.open("07 Irons HiScore").get_worksheet(1)



#BOT

bot = commands.Bot(command_prefix='!hs ')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')



@bot.command(name='add', help='Adds a player to the spreadsheets.')
@commands.has_permissions(kick_members=True)
async def add(ctx, name):
    names = [x.lower() for x in bosses_sheet.col_values(1)[1:]]
    update_player(bosses_sheet,skills_sheet,names,name,1)
    response = f"{name} has been added to the memberslist."
    await ctx.send(response)

@bot.command(name='update', help='Updates a players stats in the spreadsheets.')
@commands.has_permissions(kick_members=True)
async def update(ctx, name):
    names = [x.lower() for x in bosses_sheet.col_values(1)[1:]]
    update_player(bosses_sheet,skills_sheet,names,name,0)
    response = f"{name} stats has been updated."
    await ctx.send(response)

@bot.command(name='change', help='Changes a players rsn in the spreadsheets.')
@commands.has_permissions(kick_members=True)
async def change_rsn(ctx, old_name,new_name):
    names = [x.lower() for x in bosses_sheet.col_values(1)[1:]]
    update_rsn(bosses_sheet,skills_sheet,names,old_name,new_name)
    response = f"{old_name} has been changed to {new_name} and his stats has been updated."
    await ctx.send(response)

@bot.command(name='fullupdate', help='Updates every player.')
@commands.has_permissions(kick_members=True)
async def full_update(ctx):
    msg = f"All players are being updated ..."
    await ctx.send(msg)
    names = [x.lower() for x in bosses_sheet.col_values(1)[1:]]
    update_all(bosses_sheet,skills_sheet,names)
    response = f"All players have been updated."
    await ctx.send(response)

@bot.command(name='top', help='Shows the top 5 players and their kc for a specific stat.')
async def top(ctx, stat):
    names = [x.lower() for x in bosses_sheet.col_values(1)[1:]]
    top_stats = top_stat(bosses_sheet, skills_sheet, names, stat, 5)
    if top_stats != 404:
        stat = get_stat(stat)
        response = f"{stat}\n\n"
        for player in top_stats:
            if len(player) == 2:
                response += f"{player[1]} {player[0]}\n"
            elif len(player) == 3:
                response += f"{player[2]} {player[1]} {player[0]}\n"
    else:
        response = f"Stat {stat} not found."
    await ctx.send(response)

@bot.command(name='compare', help='Shows the top 5 players and their kc for a specific stat.')
async def compare(ctx, stat, player1, player2):
    names = [x.lower() for x in bosses_sheet.col_values(1)[1:]]
    compare_players(bosses_sheet, skills_sheet, names, player1, player2, stat)
    response = a

#
#
# @bot.command(name='remove',help ='Removes Corner role from a specific member.')
# @commands.has_permissions(kick_members=True)
# async def remove_corners(ctx, member:discord.Member):
#     role = discord.utils.get(ctx.guild.roles, name="Corner")
#     await member.remove_roles(role)
#
# @bot.command(name='reset', help ='Removes Corner role from every member.')
# @commands.has_permissions(kick_members=True)
# async def remove_corners(ctx):
#     role = discord.utils.get(ctx.guild.roles, name="Corner")
#     for member in ctx.guild.members:
#         await member.remove_roles(role)
#
# @bot.command(name='members')
# @commands.has_permissions(kick_members=True)
# async def remove_corners(ctx):
#     role = discord.utils.get(ctx.guild.roles, name="Corner")
#     members_in_corner = ''
#     for member in ctx.guild.members:
#         if role in member.roles:
#             name = member.nick if member.nick else member.name
#             members_in_corner += f'{name}\n'
#     if members_in_corner == '':
#         members_in_corner = 'No members in the corner.'
#     await ctx.send(members_in_corner)



bot.run(token)
