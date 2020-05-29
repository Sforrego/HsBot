@bot1.command(name="startbingo00",help="starts tracking every player participating in the bingo.")
@commands.has_permissions(kick_members=True)
async def start_teams(ctx):
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
async def check_team(ctx, team):
    try:
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    except gspread.exceptions.APIError as e:
        client.login()
        names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    mydict = bingo_check(bingo_sheet_bosses,bingo_sheet_skills,team)
    response = ""
    for key, value in mydict.items():
        if len(value) == 2:
            response += f"{key}: {value[0]}/{value[1]} ({int(value[0])/int(value[1])*100:.2f}%)\n"
        else:
            response += f"{key}: {value[0]}\n"
    response += "\n\nBoss KC might not be accurate (if you weren't ranked in the highscores in that boss when bingo began)"
    await ctx.send(response)
