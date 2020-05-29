import gspread
from oauth2client.service_account import ServiceAccountCredentials
from getstats import *
from constants import *
import time
import asyncio
from datetime import datetime
import itertools

def get_stat(name):
    name = name.lower()
    if name in NAMES_LOWER:
        return NAMES_LOWER[name]
    elif name in boss_shorts:
        return boss_shorts[name]
    else:
        return 0

def get_stats_shorts():
    newdict = {stat:[] for stat in BOSSES}
    for stat in CLUES:
        newdict[stat] = []
    for stat_short, stat in boss_shorts.items():
        newdict[stat].append(stat_short)
    newdict = {key:value for key,value in newdict.items() if value != [] }
    return newdict

def get_pretty_names(start_sheet,names):
    pretty_names_list = []
    ugly_names = start_sheet.col_values(2)[1:]
    pretty_names = start_sheet.col_values(1)[1:]
    for name in names:
        index = ugly_names.index(name)
        pretty_name = pretty_names[index]
        pretty_name = pretty_name.replace("_"," ")
        pretty_names_list.append(pretty_name)
    return pretty_names_list


def get_stat_top(bosses_sheet, skills_sheet, start_sheet, names, stat, n):
    top_stats = top_stat(bosses_sheet, skills_sheet, names, stat, n)
    if top_stats != 404:
        stat = get_stat(stat)
        response = f'{stat}\n\n'
        players = [x[-1] for x in top_stats]
        players = get_pretty_names(start_sheet,players)
        for i,player in enumerate(top_stats,start=1):
            if len(player) == 2:
                response += f"{i}. {players[i-1]} {player[0]} \n"
            elif len(player) == 3:
                response += f"{i}.  {players[i-1]} {player[0]} {player[1]}\n"
    else:
        response = f"Stat {stat} not found."
    response += "\n"
    return response

def get_tracked_top(tracked_sheet,start_sheet, names, stat, n):
    top_stats = top_tracked(tracked_sheet, names, stat, n)
    if top_stats != 404:
        stat = get_stat(stat)
        response = f'{stat}\n\n'
        players = [x[-1] for x in top_stats]
        players = get_pretty_names(start_sheet,players)
        for i,player in enumerate(top_stats,start=1):
            if len(player) == 2:
                response += f"{i}. {players[i-1]} {player[0]} \n"
            elif len(player) == 3:
                response += f"{i}.  {players[i-1]} {player[0]} {player[1]}\n"
    else:
        response = f"Stat {stat} not found."
    response += "\n"
    return response

def top_stat(bosses_sheet, skills_sheet, names, stat, n):
    stat = get_stat(stat)
    if stat == 404:
        return stat
    elif stat not in SKILLS:
        index = STATSINDEX[stat]
        mylist = bosses_sheet.col_values(index)[1:]
        mylist = [(int(mylist[i]),names[i]) if mylist[i] != "" else (-1,names[i]) for i in range(len(mylist))]
    elif stat in SKILLS:
        index = SKILLS.index(stat)*2+2
        lvl = skills_sheet.col_values(index)[1:]
        xp = skills_sheet.col_values(index+1)[1:]
        mylist = list(zip(xp,lvl))
        mylist = [(int(mylist[i][1]),int(mylist[i][0]),names[i]) if mylist[i][0] != "" else (-1,names[i]) for i in range(len(mylist))]

    mylist = sorted(mylist, reverse=True)
    mylist = mylist[:n]
    return mylist

def top_tracked(tracked_sheet, names, stat, n):
    stat = get_stat(stat)
    if stat == 404:
        return stat
    elif stat in SKILLS:
        index = SKILLS.index(stat)+1
        xp = tracked_sheet.col_values(index+1)[1:]
        mylist = [(int(value),name) if value != "" else (-1,name) for value,name in zip(xp,names)]

    mylist = sorted(mylist, reverse=True)
    mylist = mylist[:n]
    return mylist

def update_player(bosses_sheet, skills_sheet, start_sheet, names, name, stats, addplayer=0):
    name = name.lower()
    if name not in names and not addplayer:
        print("Player not in memberslist.")
    elif name in names and addplayer:
        print("Player already in memberslist.")
    else:
        if stats != 404:

            index = names.index(name)+2


            skills_cell_list = skills_sheet.range(f'B{index}:AW{index}')
            bosses_cell_list = bosses_sheet.range(f'B{index}:BA{index}')
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            player_bosses = [player_skills["Overall"]]+list(player_clues.values())+list(player_bosses.values())

            if addplayer:
                start_cell_list = start_sheet.range(f'B{index}:F{index}')
                date_cell_list = start_sheet.range(f'H{index}:I{index}')
                mylist = [name.replace(" ","_"),player_skills["Overall"],
                player_skills["Overall"],player_skills["Overall_Xp"],player_skills["Overall_Xp"]]
                start_cell_list[0].value = mylist[0]
                for i,cell in enumerate(start_cell_list[1:],start=1):
                    cell.value = int(mylist[i])
                today = datetime.now()
                today = today.strftime("%Y/%m/%d")
                for i,cell in enumerate(date_cell_list):
                    cell.value = today
                start_sheet.update_cells(start_cell_list)
                start_sheet.update_cells(date_cell_list)


            else:
                start_cell_list = start_sheet.range(f'D{index}:D{index}')
                start_cell_list.extend(start_sheet.range(f'F{index}:F{index}'))
                date_cell_list = start_sheet.range(f'I{index}:I{index}')
                mylist = [player_skills["Overall"],player_skills["Overall_Xp"]]
                for i,cell in enumerate(start_cell_list):
                    cell.value = int(mylist[i])
                today = datetime.now()
                today = today.strftime("%Y/%m/%d")
                for i,cell in enumerate(date_cell_list):
                    cell.value = today
                start_sheet.update_cells(start_cell_list)
                start_sheet.update_cells(date_cell_list)

            player_skills = list(player_skills.values())
            print(f"updating {name} total {player_skills[0]}")


            for j,cell in enumerate(skills_cell_list):
                cell.value = int(player_skills[j])
            for j,cell in enumerate(bosses_cell_list):
                cell.value = int(player_bosses[j])

            skills_sheet.update_cells(skills_cell_list)
            bosses_sheet.update_cells(bosses_cell_list)


        else:
            print(f"{name} not found in hiscores.")

def update_rsn(members_sheet,bosses_sheet, skills_sheet, start_sheet, names, old_name, new_name):
    old_name = old_name.lower()
    if old_name in names:
        index = names.index(old_name)+2
        members_sheet.update_acell(f"K{index}",new_name)
        names[index-2] = new_name.lower()
        stats = getStats(playerURL(new_name,'iron'))
        update_player(bosses_sheet, skills_sheet, start_sheet, names, new_name, stats)

def check(names,rsn):
    if rsn.lower() in names:
        return True
    return False

def bingo_update(bingo_sheet_bosses,bingo_sheet_skills,skills=0,init=0):
    if not skills:
        bingo_list = BINGO_BOSSES
        starting_col = "E"
        last_col = "AW"
        bingo_sheet = bingo_sheet_bosses
    elif skills == 1:
        bingo_list = BINGO_SKILLS
        starting_col = "B"
        last_col = "AB"
        bingo_sheet = bingo_sheet_skills

    names = bingo_sheet_bosses.col_values(1)[1:]
    team_indexs = []

    for i,name in enumerate(names):
        if "team" in name.lower():
            team_indexs.append(i+2)

    if skills != "both":
        ncols = len(bingo_list)

        bingo_cell_list = bingo_sheet.range(f'{starting_col}{2}:{last_col}{len(names)+1}')

        new_bingo_list = []
        for index3,cell in enumerate(bingo_cell_list):
            modifier = 0 if init else 1
            if index3 % 3 == modifier:
                if cell.row in team_indexs:
                    pass
                else:
                    new_bingo_list.append(cell)
        names = [x for x in names if "team" not in x.lower() ]
        for index, name in enumerate(names):
            stats = getStats(playerURL(name,'iron'))
            if stats == 404:
                print(f"{name} not found")
            else:
                print(f"{index+1}. Updating {name}")
                player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
                for index2, value in enumerate(bingo_list):
                    cell = new_bingo_list[ncols*index+index2]
                    if skills:
                        cell.value = int(player_skills[f"{value}_Xp"])
                    else:
                        cell.value = int(player_bosses[value]) if int(player_bosses[value]) != -1 else 0


        bingo_sheet.update_cells(new_bingo_list)
    else:
        bingo_list = [BINGO_BOSSES,BINGO_SKILLS]
        starting_col = ["E","B"]
        last_col = ["AW","AB"]
        bingo_sheet = [bingo_sheet_bosses,bingo_sheet_skills]
        ncols = [len(bingo_list[0]),len(bingo_list[1])]
        bingo_cell_list = [bingo_sheet[i].range(f'{starting_col[i]}{2}:{last_col[i]}{len(names)+1}') for i in range(2)]
        new_bingo_list = [[],[]]

        for index3,cell, in enumerate(bingo_cell_list[0]):
            modifier = 0 if init else 1
            if index3 % 3 == modifier:
                if cell.row in team_indexs:
                    pass
                else:
                    new_bingo_list[0].append(cell)
        for index3,cell, in enumerate(bingo_cell_list[1]):
            modifier = 0 if init else 1
            if index3 % 3 == modifier:
                if cell.row in team_indexs:
                    pass
                else:
                    new_bingo_list[1].append(cell)

        names = [x for x in names if "team" not in x.lower() ]
        for index, name in enumerate(names):
            stats = getStats(playerURL(name,'iron'))
            if stats == 404:
                print(f"{name} not found")
            else:

                print(f"{index+1}. Updating {name}")
                player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
                for index2, value in enumerate(bingo_list[0]):
                    cell1 = new_bingo_list[0][ncols[0]*index+index2]
                    cell1.value = int(player_bosses[value]) if int(player_bosses[value]) != -1 else 0
                for index2, value in enumerate(bingo_list[1]):
                    cell2 = new_bingo_list[1][ncols[1]*index+index2]
                    cell2.value = int(player_skills[f"{value}_Xp"])

        bingo_sheet[0].update_cells(new_bingo_list[0])
        bingo_sheet[1].update_cells(new_bingo_list[1])
    print("Finished updating.")

def bingo_check(bingo_sheet_bosses,bingo_sheet_skills,team):
    list_of_skills = bingo_sheet_skills.get_all_values()
    list_of_bosses = bingo_sheet_bosses.get_all_values()
    team_index = (int(team)-1)*7+1
    row = list_of_skills[team_index]
    row2 =  list_of_bosses[team_index]
    progress = {}
    for i,skill in enumerate(BINGO_SKILLS,start=1):
        fraction = round(int(row[3*i])/Bingo_SKILL_TILES[skill],2)
        if fraction >= 1:
            progress[skill] = ("COMPLETED",)
        else:
            progress[skill] = (row[3*i],Bingo_SKILL_TILES[skill])
        #print(fraction)
    for i,boss in enumerate(BINGO_BOSS_TILES.keys(),start=1):
        if i < 4:
            kc = row2[i]
            fraction = round(int(kc)/BINGO_BOSS_TILES[boss],2)
        else:
            kc = row2[3*(i-3)+3]
            fraction = round(int(kc)/BINGO_BOSS_TILES[boss],2)

        if fraction >= 1:
            progress[boss] = ("COMPLETED",)
        else:
            if boss in ["Chaos Fanatic","Scorpia","Crazy Archaeologist"]:
                progress[boss] = (kc,)
            else:
                progress[boss] = (kc,BINGO_BOSS_TILES[boss])

    print(progress)
    return progress
def update_all(bosses_sheet, skills_sheet, start_sheet, client, starting_cell=2, tracker_sheet=None):
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    bosses_values = bosses_sheet.get_all_values()[1:]
    skills_values = skills_sheet.get_all_values()[1:]
    start_values = start_sheet.get_all_values()[1:]
    bosses_list = []
    skills_list = []
    start_list_lvl = []
    start_list_xp = []

    if tracker_sheet:
        tracker_values = tracker_sheet.get_all_values()[1:]
        tracker_list = []
        date_cell_list2 = tracker_sheet.range(f'AX2:AX{len(names)+1}')
        tracker_cell_list = tracker_sheet.range(f'B{starting_cell}:AW{len(names)+1}')
    # start_list = []
    bosses_cell_list = bosses_sheet.range(f'B{starting_cell}:BA{len(names)+1}')
    skills_cell_list = skills_sheet.range(f'B{starting_cell}:AW{len(names)+1}')
    start_cell_list = start_sheet.range(f'D{starting_cell}:D{len(names)+1}')
    start_cell_list.extend(start_sheet.range(f'F{starting_cell}:F{len(names)+1}'))
    # start_cell_list = start_sheet.range(f'C{starting_cell}:F{len(names)+1}')
    date_cell_list = start_sheet.range(f'I{starting_cell}:I{len(names)+1}')
    not_found = []
    outdated_names = start_sheet.range(f'J{starting_cell}:J{len(names)+1}')

    for index,name in enumerate(names[starting_cell-2:], start=starting_cell):
        stats = getStats(playerURL(name,'iron'))
        if stats != 404:
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            player_bosses = [player_skills["Overall"]]+list(player_clues.values())+list(player_bosses.values())
            # start_list.append((player_skills["Overall"],player_skills["Overall"],player_skills["Overall_Xp"],player_skills["Overall_Xp"]))
            if tracker_sheet:
                temp_list =  [value for key,value in player_skills.items() if "Xp" in key]
                tracker_list.append([x for pair in zip(temp_list,temp_list) for x in pair])


            player_skills = list(player_skills.values())
            print(f"updating {index}. {name} total {player_skills[0]} xp {player_skills[1]}")
            bosses_list.append(player_bosses)
            skills_list.append(player_skills)
            start_list_lvl.append(player_skills[0])
            start_list_xp.append(player_skills[1])


        else:

            print(f"{name} not found in highscores.")
            bosses_list.append(bosses_values[index-2][1:])
            skills_list.append(["" for i in range(48)])
            # start_list.append([int(x) if x else x for x in start_values[index-2][2:6]])
            start_list_lvl.append(start_values[index-2][3])
            start_list_xp.append(start_values[index-2][5])
            if tracker_sheet:
                tracker_list.append(tracker_values[index-2][1:-2])
            not_found.append(name)

    bosses_list = [item for sublist in bosses_list for item in sublist]
    skills_list = [item for sublist in skills_list for item in sublist]
    start_list = start_list_lvl+start_list_xp
    if tracker_sheet:
        tracker_list = [int(item) if item != "" else item for sublist in tracker_list for item in sublist]
        for i, val in enumerate(tracker_list):
            if val:
                print(tracker_cell_list[i].value, val)
                tracker_cell_list[i].value = int(val)
                if tracker_cell_list[i].value:
                        tracker_cell_list[i].value = int(tracker_cell_list[i].value)



    for i, val in enumerate(bosses_list):
        if val:
            bosses_cell_list[i].value = int(val)

    for i, val in enumerate(skills_list):
        skills_cell_list[i].value = int(val) if val != "" else ""

    for i, val in enumerate(start_list):
        if val:
            start_cell_list[i].value = int(val)

    today = datetime.now()
    today = today.strftime("%Y/%m/%d")

    for i, val in enumerate(date_cell_list):
        date_cell_list[i].value = today

    for i,_ in enumerate(outdated_names):
        if len(not_found) > i:
            val = not_found[i]
        else:
            val = ""
        outdated_names[i].value = val


    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    bosses_sheet.update_cells(bosses_cell_list)
    skills_sheet.update_cells(skills_cell_list)
    start_sheet.update_cells(start_cell_list)
    start_sheet.update_cells(date_cell_list)
    start_sheet.update_cells(outdated_names)

    print("Sheets updated.")
    return not_found

def tracker(tracker_sheet, start_sheet, client, start=0,starting_cell=2):
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    tracker_values = tracker_sheet.get_all_values()[1:]
    tracker_list = []
    if start:
        date_cell_list = tracker_sheet.range(f'AX2:AX{len(names)+1}')
    else:
        date_cell_list = tracker_sheet.range(f'AY2:AY{len(names)+1}')
    # start_list = []
    tracker_cell_list = tracker_sheet.range(f'B{starting_cell}:AW{len(names)+1}')
    # start_cell_list = start_sheet.range(f'C{starting_cell}:F{len(names)+1}')
    not_found = []

    for index,name in enumerate(names[starting_cell-2:], start=starting_cell):
        stats = getStats(playerURL(name,'iron'))
        if stats != 404:
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            # start_list.append((player_skills["Overall"],player_skills["Overall"],player_skills["Overall_Xp"],player_skills["Overall_Xp"]))
            player_skills = [value for key,value in player_skills.items() if "Xp" in key]

            player_skills = [x for pair in zip(player_skills,player_skills) for x in pair]

            print(f"updating {index}. {name} total {player_skills[0]} xp {player_skills[1]}")
            tracker_list.append(player_skills)
        else:

            print(f"{name} not found in highscores.")
            tracker_list.append(tracker_values[index-2][1:-2])
            not_found.append(name)

    tracker_list = [int(item) if item != "" else item for sublist in tracker_list for item in sublist]

    for i, val in enumerate(tracker_list):
        if val:
            if not start:
                if i%2==1:
                    tracker_cell_list[i].value = int(val)
            else:
                tracker_cell_list[i].value = int(val)
            if tracker_cell_list[i].value:
                tracker_cell_list[i].value = int(tracker_cell_list[i].value)


    today = datetime.now()
    today = today.strftime("%Y/%m/%d")
    for cell in date_cell_list:
        cell.value = today


    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    tracker_sheet.update_cells(tracker_cell_list)
    tracker_sheet.update_cells(date_cell_list)


    print("Trackers updated.")
    return not_found

def update_bosses_names(BOSSES, sheet):
    # updates the columns names
    for i, boss in enumerate(BOSSES):
        sheet.update_cell(1, 10+i, boss)

def compare_players(bosses_sheet, skills_sheet, names, name1, name2, stat):
    name1,name2 = name1.lower(),name2.lower()
    index1 = names.index(name1)
    index2 = names.index(name2)
    if stat in BOSSES+CLUES:
        index = STATSINDEX[stat]
        boss = bosses_sheet.col_values(index)[1:]
        score1,score2 = int(boss[index1]),int(boss[index2])
        return   (1, score1,score2) if score1>score2 else (0,score1,score2)
    elif stat in SKILLS:
        index = SKILLS.index(stat)*2+2
        skill = skills_sheet.col_values(index)[1:]
        skill_xp = skills_sheet.col_values(index+1)[1:]
        xp1,xp2 = int(skill_xp[index1]),int(skill_xp[index2])
        lvl1,lvl2 = int(skill[index1]),int(skill[index2])
        return   (1, xp1,lvl1,xp2,lvl2) if xp1>xp2 else (0,xp1,lvl1,xp2,lvl2)
    else:
        return 404

def remove_players(bosses_sheet, skills_sheet, start_sheet, names, to_remove):
    for name in to_remove:
        name = name.lower()
        if name not in names:
            print("Player not in memberlist.")
        else:
            index = names.index(name)+2
            names.remove(name)
            start_sheet.delete_row(index)
            skills_sheet.delete_row(index)
            bosses_sheet.delete_row(index)

def player_top_stats(bosses_sheet, skills_sheet, start_sheet, names, name, bosses):
    sheet = bosses_sheet if bosses else skills_sheet
    stat = CLUES+BOSSES if bosses else SKILLS
    name = name.lower()
    index_name = names.index(name)+1
    list_of_lists = sheet.get_all_values()
    transposed = list(map(list, zip(*list_of_lists)))[1:]
    transposed = [[i if i != "" else -1 for i in x] for x in transposed]
    print(transposed)
    sorted_list = [sorted(map(int,x[1:]),reverse=True) for x in transposed]
    player = list_of_lists[index_name]
    top_stats = {}
    for i,stat in enumerate(player[1:]):
        stat = int(stat)
        if stat != -1:
            index_in_stat = sorted_list[i].index(stat)
            top_stats[list_of_lists[0][i+1]] = index_in_stat+1 # +1 so the ranks start at 1
    if not bosses:
        overall = top_stats["Overall"]
        top_stats = {key.replace("_Xp",""):value for key,value in top_stats.items() if "_Xp" in key}
        top_stats["Overall"] = overall
    return top_stats


def get_coded_name(start_sheet):
    names = [x.lower().replace(" ","_") for x in start_sheet.col_values(1)[1:]]
    cell_list = start_sheet.range(f'B2:B{len(names)+1}')
    for i,cell in enumerate(cell_list):
        cell.value = names[i]
    start_sheet.update_cells(cell_list)

def new_remove(members, start_sheet,bosses_sheet,skills_sheet,members_sheet):
    not_found = []

    for name in members:
        if name.lower() not in names:
            not_found.append(name)
        else:

            index = names.index(name.lower())+2
            names.remove(name.lower())
            start_sheet.delete_rows(index)
            bosses_sheet.delete_rows(index)
            members_sheet.delete_rows(index)
            skills_sheet.delete_rows(index)

    found = [x for x in members if x not in not_found]
    return found

if __name__ == "__main__":
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

    names = start_sheet.col_values(2)[1:]
    #bingo_sheet_bosses = client.open("Lockdown Bingo").worksheet('BossTracker')
    #bingo_sheet_skills = client.open("Lockdown Bingo").worksheet('SkillsTracker')
    #player_top_stats(bosses_sheet, skills_sheet, start_sheet, names, "IronRok", 1)
    #bingo_update(bingo_sheet_bosses,bingo_sheet_skills,skills=1)
    #bingo_update(bingo_sheet_bosses,bingo_sheet_skills,skills="both",init=1)
    #bingo_check(bingo_sheet_bosses,bingo_sheet_skills,5)
    #EXAMPLES
    stats = getStats(playerURL('eehaap','iron'))
    update_player(bosses_sheet,skills_sheet,start_sheet,names,"eehaap",stats,1)
    # tracker(tracker_sheet,start_sheet,client)
    #print(get_tracked_top(tracked_sheet,start_sheet,names,"overall",10))

    #get_coded_name(start_sheet)
    # print(new_remove(["Idiotium","Iron_Man_MkV","asdqwe","ironn_69","siphiwe_moyo","iron_lyfeee","weeeeeeeee"],start_sheet,bosses_sheet,skills_sheet,members_sheet))
    #update_all(bosses_sheet,skills_sheet,start_sheet,client,tracker_sheet=tracker_sheet)
    #update_player(bosses_sheet,skills_sheet,start_sheet,names,"hassinen42")
    #update_player(bosses_sheet,skills_sheet,start_sheet,names,"bonerrific",1)
    # print(top_stat(bosses_sheet,skills_sheet,names,"Zulrah",10))
    #print(get_pretty_name(start_sheet,"no_ge_canvey"))
    #print(compare_players(bosses_sheet, skills_sheet, names, "IronRok", "no ge canvey", "Attack"))

    #print(skills_sheet.col_values(1))
    # pretty = get_pretty_names2(start_sheet)
    # start_cell_list = start_sheet.range(f'B{2}:B{358}')
    # for index,cell in enumerate(start_cell_list):
    #     cell.value = pretty[index]
    # start_sheet.update_cells(start_cell_list)
