import gspread
from oauth2client.service_account import ServiceAccountCredentials
from getstats import *
from constants import *
import time
import asyncio


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
    for name in names:
        ugly_names = start_sheet.col_values(2)[1:]
        pretty_names = start_sheet.col_values(1)[1:]
        index = ugly_names.index(name)
        pretty_names_list.append(pretty_names[index])
    return pretty_names_list

def get_stat_top(bosses_sheet, skills_sheet, start_sheet, names, stat, n):
    top_stats = top_stat(bosses_sheet, skills_sheet, names, stat, n)
    if top_stats != 404:
        stat = get_stat(stat)
        response = f"{stat}\n\n"
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
            bosses_cell_list = bosses_sheet.range(f'B{index}:AZ{index}')
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            player_bosses = [player_skills["Overall"]]+list(player_clues.values())+list(player_bosses.values())

            if addplayer:
                start_cell_list = start_sheet.range(f'B{index}:F{index}')
                mylist = [name.replace(" ","_"),player_skills["Overall"],
                player_skills["Overall"],player_skills["Overall_Xp"],player_skills["Overall_Xp"]]
                for i,cell in enumerate(start_cell_list):
                    cell.value = int(mylist[i])
                start_sheet.update_cells(start_cell_list)
            else:
                start_cell_list = start_sheet.range(f'D{index}:D{index}')
                start_cell_list.extend(start_sheet.range(f'F{index}:F{index}'))
                mylist = [player_skills["Overall"],player_skills["Overall_Xp"]]
                for i,cell in enumerate(start_cell_list):
                    cell.value = int(mylist[i])
                start_sheet.update_cells(start_cell_list)

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
        names[index] = new_name
        update_player(bosses_sheet, skills_sheet, start_sheet, names, new_name)


def update_all(bosses_sheet, skills_sheet, start_sheet, starting_cell=2):
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]
    bosses_values = bosses_sheet.get_all_values()[1:]
    skills_values = skills_sheet.get_all_values()[1:]
    start_values = start_sheet.get_all_values()[1:]
    bosses_list = []
    skills_list = []
    start_list = []
    bosses_cell_list = bosses_sheet.range(f'B{starting_cell}:AZ{len(names)+1}')
    skills_cell_list = skills_sheet.range(f'B{starting_cell}:AW{len(names)+1}')
    start_cell_list = start_sheet.range(f'D{starting_cell}:D{len(names)+1}')
    start_cell_list.extend(start_sheet.range(f'F{starting_cell}:F{len(names)+1}'))
    # start_cell_list = start_sheet.range(f'C{starting_cell}:F{len(names)+1}')
    not_found = []


    for index,name in enumerate(names[starting_cell-2:], start=starting_cell):
        stats = getStats(playerURL(name,'iron'))
        if stats != "404":
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            player_bosses = [player_skills["Overall"]]+list(player_clues.values())+list(player_bosses.values())
            start_list.append((player_skills["Overall"],player_skills["Overall_Xp"]))
            # start_list.append((player_skills["Overall"],player_skills["Overall"],player_skills["Overall_Xp"],player_skills["Overall_Xp"]))



            player_skills = list(player_skills.values())
            print(f"updating {name} total {player_skills[0]}")
            bosses_list.append(player_bosses)
            skills_list.append(player_skills)
        else:

            print(f"{name} not found in highscores.")
            bosses_list.append(bosses_values[index-2][1:])
            skills_list.append(skills_values[index-2][1:])
            # start_list.append((int(start_values[index-2][3]),int(int(start_values[index-2][5]))))
            start_list.append([int(x) for x in start_values[index-2][2:6]])
            print([int(x) for x in start_values[index-2][2:6]])

            not_found.append(name)

    bosses_list = [item for sublist in bosses_list for item in sublist]
    skills_list = [item for sublist in skills_list for item in sublist]
    start_list = [item for sublist in start_list for item in sublist]


    for i, val in enumerate(bosses_list):  #gives us a tuple of an index and value
        if val:
            bosses_cell_list[i].value = int(val)

    for i, val in enumerate(skills_list):  #gives us a tuple of an index and value
        if val:
            skills_cell_list[i].value = int(val)

    for i, val in enumerate(start_list):  #gives us a tuple of an index and value
        if val:
            start_cell_list[i].value = int(val)

    bosses_sheet.update_cells(bosses_cell_list)
    skills_sheet.update_cells(skills_cell_list)
    start_sheet.update_cells(start_cell_list)


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

if __name__ == "__main__":
    scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    bosses_sheet = client.open("07 Irons HiScore").get_worksheet(0)
    skills_sheet = client.open("07 Irons HiScore").get_worksheet(1)
    start_sheet = client.open("07 Irons HiScore").get_worksheet(2)
    names = [x.lower() for x in start_sheet.col_values(2)[1:]]

    #update_all(bosses_sheet,skills_sheet,start_sheet,names,233)
    #update_player(bosses_sheet,skills_sheet,start_sheet,names,"big_win")

    #print(get_pretty_name(start_sheet,"no_ge_canvey"))

    #print(compare_players(bosses_sheet, skills_sheet, names, "IronRok", "no ge canvey", "Attack"))
    #print(skills_sheet.col_values(1))
    #not_found = update_all(bosses_sheet,skills_sheet,names)
    #print(compare_players(bosses_sheet,skills_sheet,names,"no ge canvey","ironrok","Magic"))
    #print(top_stat(bosses_sheet,skills_sheet,names,"Zulrah",7))
