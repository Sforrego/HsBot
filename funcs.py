import gspread
from oauth2client.service_account import ServiceAccountCredentials
from getstats import *
from constants import *
import time
import asyncio
from datetime import datetime
import itertools

def get_stat(stat):
    stat = stat.lower()
    if stat in NAMES_LOWER:
        return NAMES_LOWER[stat]
    elif stat in boss_shorts:
        return boss_shorts[stat]
    else:
        raise Exception(f"{stat} is not a valid stat.")

def get_stats_shorts():
    newdict = {stat:[] for stat in BOSSES}
    for stat in CLUES:
        newdict[stat] = []
    for stat_short, stat in boss_shorts.items():
        newdict[stat].append(stat_short)
    newdict = {key:value for key,value in newdict.items() if value != [] }
    return newdict

def get_pretty_names(members_sheet,names):
    pretty_names_list = []
    ugly_names = members_sheet.col_values(11)[1:]
    pretty_names = members_sheet.col_values(10)[1:]
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

def get_tracked_top(tracked_sheet,start_sheet, names, stat, n,tracked_players):
    top_stats = top_tracked(tracked_sheet, names, stat, n,tracked_players)
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
    print("stat")
    mylist = sorted(mylist, reverse=True)
    mylist = mylist[:n]
    return mylist

def top_tracked(tracked_sheet, names, stat, n,tracked_players):
    stat = get_stat(stat)
    if stat == 404:
        return stat
    elif stat in SKILLS:
        index = SKILLS.index(stat)+1
        xp = tracked_sheet.col_values(index+1)[1:]
        mylist = [(int(value),name) if value != "" else (-1,name) for value,name in zip(xp,names) if name in tracked_players]

    mylist = sorted(mylist, reverse=True)
    mylist = mylist[:n]
    return mylist

def tracked_player(tracked_sheet, names, stat, name):
    stat = get_stat(stat)
    if stat == 404:
        return stat
    elif stat in SKILLS:
        index = SKILLS.index(stat)+1
        xp = tracked_sheet.col_values(index+1)[1:]
        mylist = [(int(value),name) if value != "" else (-1,name) for value,name in zip(xp,names)]

    #mylist = sorted(mylist, reverse=True)
    mylist = mylist[names.index(name)]
    return mylist

def update_player(bosses_sheet, skills_sheet, start_sheet, names, name, stats, addplayer=0,tracker_sheet=None):
    name = name.lower()
    if name not in names and not addplayer:
        print("Player not in memberslist.")

    else:
        if stats != 404:

            index = names.index(name)+2

            if tracker_sheet:
                print("There is tracker sheet!")
                date_cell_list2 = tracker_sheet.range(f'AX{index}:AX{index}')
                tracker_cell_list = tracker_sheet.range(f'B{index}:AW{index}')




            skills_cell_list = skills_sheet.range(f'B{index}:AW{index}')
            bosses_cell_list = bosses_sheet.range(f'B{index}:BA{index}')
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))

            if tracker_sheet:
                temp_list =  [value for key,value in player_skills.items() if "Xp" in key]
                tracked_player_stats  = temp_list
                print(tracked_player_stats)
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
            if tracker_sheet:
                tracker_cell_list = [x for i,x in enumerate(tracker_cell_list) if i%2==0 ]
                for i,val in enumerate(tracked_player_stats):
                    tracker_cell_list[i].value = int(val) if val else val
                    if tracker_cell_list[i].value:
                        tvar = tracker_cell_list[i].value
                        tracker_cell_list[i].value = int(tvar)
                tracker_sheet.update_cells(tracker_cell_list)
            skills_sheet.update_cells(skills_cell_list)
            bosses_sheet.update_cells(bosses_cell_list)


        else:
            print(f"{name} not found in hiscores.")

def update_rsn(members_sheet, names, old_name, new_name):
    old_name = old_name.lower()
    if old_name in names:
        index = names.index(old_name)+2
        members_sheet.update_acell(f"K{index}",new_name)
        names[index-2] = new_name.lower()
    elif new_name in names:
        raise Exception(f"{new_name} is already in the spreadsheet.")
    else:
        raise Exception(f"{old_name} is not in the spreadsheet.")
def check(names,rsn):
    if rsn.lower() in names:
        return True
    return False

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
        print("There is tracker sheet!")
        tracker_values = tracker_sheet.get_all_values()[1:]
        tracker_values = [x[:-2] for x in tracker_values]
        tracker_list = []
        date_cell_list2 = tracker_sheet.range(f'AX{starting_cell}:AX{len(names)+1}')
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
                tracker_list.append(temp_list)


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
                #temp_list = [x for x,i in enumerate(tracker_values[index-2][1:-2]) if i%2==0]
                tracker_list.append(["" for i in range(24)])
            not_found.append(name)

    bosses_list = [item for sublist in bosses_list for item in sublist]
    skills_list = [item for sublist in skills_list for item in sublist]
    start_list = start_list_lvl+start_list_xp

    if tracker_sheet:
        tracker_cell_list = [x for i,x in enumerate(tracker_cell_list) if i%2==0 ]
        tracker_list = [int(item) if item != "" else item for sublist in tracker_list for item in sublist]
        for i, val in enumerate(tracker_list):
            #print(tracker_cell_list[i].value, val)
            tracker_cell_list[i].value = int(val) if val else val
            if tracker_cell_list[i].value:
                tvar = tracker_cell_list[i].value
                tracker_cell_list[i].value = int(tvar)

        today = datetime.now()
        today = today.strftime("%Y/%m/%d")
        for cell in date_cell_list2:
            cell.value = today

        tracker_sheet.update_cells(tracker_cell_list)
        tracker_sheet.update_cells(date_cell_list2)

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

def get_tiles_done(bingo_sheet, team_num):
    tiles = bingo_sheet.col_values(1)[1:26]
    team_tiles = bingo_sheet.col_values(team_num+1)[1:26]
    tiles_done = [tiles[i] for i in range(len(team_tiles)) if team_tiles[i] == "DONE"]
    tiles_num = [i for i in range(len(team_tiles)) if team_tiles[i] == "DONE"]
    return tiles_done,tiles_num

def get_tiles_left(bingo_sheet, team_num):
    tiles = bingo_sheet.col_values(1)[1:26]
    team_tiles = bingo_sheet.col_values(team_num+1)[1:26]
    tiles_left = [tiles[i] for i in range(len(team_tiles)) if team_tiles[i] != "DONE"]

    return tiles_left

def get_number_tiles_left(bingo_sheet, team_num):
    tiles = bingo_sheet.col_values(1)[1:26]
    team_tiles = bingo_sheet.col_values(team_num+1)[1:26]
    tiles_left = [tiles[i] for i in range(len(team_tiles)) if team_tiles[i] == ""]
    hidden_left = 0
    hidden_tiles_left = []
    for tile in tiles_left:
        if "hidden" in tile.lower():
            hidden_left += 1
            hiddentile,numeral = tile.lower().split("hidden tile ")
            hidden_tiles_left.append(int(numeral))

    return (len(tiles_left),hidden_left,hidden_tiles_left)



def complete_tile(bingo_sheet, team_num, tile_num):
    bingo_sheet.update_cell(tile_num+1,team_num+1, "DONE")

def reveal_tile(bingo_sheet, team_num, tile_num):
    bingo_sheet.update_cell(tile_num+1,team_num+1, "REVEALED")

def undo_tile(bingo_sheet, team_num, tile_num):
    bingo_sheet.update_cell(tile_num+1,team_num+1, "")
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

    # bingo_sheet = client.open("Bingo 07irons").worksheet('Tile Tracker')
    # print(get_tiles_left(bingo_sheet, 2))
    # undo_tile(bingo_sheet, 1, 1)
    #bingo_sheet_bosses = client.open("Lockdown Bingo").worksheet('BossTracker')
    #bingo_sheet_skills = client.open("Lockdown Bingo").worksheet('SkillsTracker')
    #player_top_stats(bosses_sheet, skills_sheet, start_sheet, names, "IronRok", 1)
    #bingo_update(bingo_sheet_bosses,bingo_sheet_skills,skills=1)
    #bingo_update(bingo_sheet_bosses,bingo_sheet_skills,skills="both",init=1)
    #bingo_check(bingo_sheet_bosses,bingo_sheet_skills,5)
    #EXAMPLES
    stats = getStats(playerURL('ironrok','iron'))
    # update_player(bosses_sheet,skills_sheet,start_sheet,names,"eehaap",stats,1)
    #tracker(tracker_sheet,start_sheet,client,start=1,starting_cell=400)
    #print(get_tracked_top(tracked_sheet,start_sheet,names,"overall",10))
    # print(tracked_player(tracked_sheet,names,"agility","ironrok"))
    #get_coded_name(start_sheet)
    # print(new_remove(["Idiotium","Iron_Man_MkV","asdqwe","ironn_69","siphiwe_moyo","iron_lyfeee","weeeeeeeee"],start_sheet,bosses_sheet,skills_sheet,members_sheet))
    #update_all(bosses_sheet,skills_sheet,start_sheet,client,tracker_sheet=tracker_sheet,starting_cell=390)
    update_player(bosses_sheet,skills_sheet,start_sheet,names,"ironrok",stats,tracker_sheet=tracker_sheet)
    #update_player(bosses_sheet,skills_sheet,start_sheet,names,"bonerrific",1)
    #print(top_stat(bosses_sheet,skills_sheet,names,"tob",10))
    #print(get_pretty_name(start_sheet,"no_ge_canvey"))
    #print(compare_players(bosses_sheet, skills_sheet, names, "IronRok", "no ge canvey", "Attack"))

    #print(skills_sheet.col_values(1))
    # pretty = get_pretty_names2(start_sheet)
    # start_cell_list = start_sheet.range(f'B{2}:B{358}')
    # for index,cell in enumerate(start_cell_list):
    #     cell.value = pretty[index]
    # start_sheet.update_cells(start_cell_list)
