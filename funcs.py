import gspread
from oauth2client.service_account import ServiceAccountCredentials
from getstats import *
from constants import *
import time
import asyncio
from datetime import datetime

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
                response += f"{i}.  {players[i-1]} {player[1]} {player[0]}\n"
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
        mylist = [(int(mylist[i][0]),int(mylist[i][1]),names[i]) if mylist[i] != "" else (-1,names[i]) for i in range(len(mylist))]

    mylist = sorted(mylist, reverse=True)
    mylist = mylist[:n]
    return mylist

def update_player(bosses_sheet, skills_sheet, start_sheet, names, name, addplayer=0):
    name = name.lower()
    if name not in names and not addplayer:
        print("Player not in memberslist.")
    elif name in names and addplayer:
        print("Player already in memberslist.")
    else:
        stats = getStats(playerURL(name,'iron'))
        if stats != "404":
            if addplayer:
                bosses_sheet.append_row([name])
                names.append(name)

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

def update_rsn(bosses_sheet, skills_sheet, start_sheet, names, old_name, new_name):
    old_name = old_name.lower()
    if old_name in names:
        index = names.index(old_name)+2
        bosses_sheet.update_acell(f'A{index}', new_name)
        start_sheet.update_acell(f'B{index}', new_name.lower())
        names[index-2] = new_name.lower()

        update_player(bosses_sheet, skills_sheet, start_sheet, names, new_name)

def update_all(bosses_sheet, skills_sheet, start_sheet, starting_cell=2):
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    bosses_values = bosses_sheet.get_all_values()[1:]
    skills_values = skills_sheet.get_all_values()[1:]
    start_values = start_sheet.get_all_values()[1:]
    bosses_list = []
    skills_list = []
    start_list_lvl = []
    start_list_xp = []
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
        if stats != "404":
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            player_bosses = [player_skills["Overall"]]+list(player_clues.values())+list(player_bosses.values())
            # start_list.append((player_skills["Overall"],player_skills["Overall"],player_skills["Overall_Xp"],player_skills["Overall_Xp"]))



            player_skills = list(player_skills.values())
            print(f"updating {index}. {name} total {player_skills[0]} xp {player_skills[1]}")
            bosses_list.append(player_bosses)
            skills_list.append(player_skills)
            start_list_lvl.append(player_skills[0])
            start_list_xp.append(player_skills[1])
        else:

            print(f"{name} not found in highscores.")
            bosses_list.append(bosses_values[index-2][1:])
            skills_list.append(skills_values[index-2][1:])
            # start_list.append([int(x) for x in start_values[index-2][2:6]])
            start_list_lvl.append(start_values[index-2][3])
            start_list_xp.append(start_values[index-2][5])
            print([int(x) for x in start_values[index-2][2:6]])

            not_found.append(name)

    bosses_list = [item for sublist in bosses_list for item in sublist]
    skills_list = [item for sublist in skills_list for item in sublist]
    start_list = start_list_lvl+start_list_xp


    for i, val in enumerate(bosses_list):
        if val:
            bosses_cell_list[i].value = int(val)

    for i, val in enumerate(skills_list):
        if val:
            skills_cell_list[i].value = int(val)

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

    bosses_sheet.update_cells(bosses_cell_list)
    skills_sheet.update_cells(skills_cell_list)
    start_sheet.update_cells(start_cell_list)
    start_sheet.update_cells(date_cell_list)

    print("Sheets updated.")
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







if __name__ == "__main__":
    scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    bosses_sheet = client.open("07 Irons HiScore").worksheet('Bosses')
    skills_sheet = client.open("07 Irons HiScore").worksheet('Skills')
    start_sheet = client.open("07 Irons HiScore").worksheet('Start')
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]

    #player_top_stats(bosses_sheet, skills_sheet, start_sheet, names, "IronRok", 1)

    #EXAMPLES

    #remove_players(bosses_sheet,skills_sheet,start_sheet,names,["saund"])
    #update_all(bosses_sheet,skills_sheet,start_sheet,243)
    #update_player(bosses_sheet,skills_sheet,start_sheet,names,"hassinen42")
    #update_player(bosses_sheet,skills_sheet,start_sheet,names,"bonerrific",1)
    print(top_stat(bosses_sheet,skills_sheet,names,"Nightmare",10))
    #print(get_pretty_name(start_sheet,"no_ge_canvey"))
    #print(compare_players(bosses_sheet, skills_sheet, names, "IronRok", "no ge canvey", "Attack"))

    #print(skills_sheet.col_values(1))
