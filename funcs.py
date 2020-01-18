import gspread
from oauth2client.service_account import ServiceAccountCredentials
from getstats import *
from constants import *
import time

def get_stat(name):
    name = name.lower()
    if name in NAMES_LOWER:
        return NAMES_LOWER[name]
    elif name in boss_shorts:
        return boss_shorts[name]
    else:
        return 404





def top_stat(bosses_sheet, skills_sheet, names, stat, n):
    stat = get_stat(stat)
    if stat == 404:
        return stat
    elif stat not in SKILLS:
        index = STATSINDEX[stat]
        list = bosses_sheet.col_values(index)[1:]
        list = [(int(list[i]),names[i]) for i in range(len(list))]

    elif stat in SKILLS:
        index = SKILLS.index(stat)*2+1
        list = skills_sheet.get_all_values()[1:]
        list = [(int(x[index+1]),x[index],x[0]) for x in list]

    list = sorted(list, reverse=True)
    list = list[:n]
    return list


def update_player(bosses_sheet, skills_sheet, names, name, addplayer=0):
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
            bosses_cell_list = bosses_sheet.range(f'B{index}:AX{index}')
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            player_bosses = [player_skills["Overall"]]+list(player_clues.values())+list(player_bosses.values())
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


def update_rsn(bosses_sheet, skills_sheet, names, old_name, new_name):
    old_name = old_name.lower()
    if old_name in names:
        index = names.index(old_name)+2
        bosses_sheet.update_acell(f'A{index}', new_name)
        update_player(bosses_sheet, skills_sheet, names, new_name)


def update_all(bosses_sheet, skills_sheet, names, starting_cell=2):
    bosses_values = bosses_sheet.get_all_values()[1:]
    skills_values = skills_sheet.get_all_values()[1:]
    bosses_list = []
    skills_list = []
    bosses_cell_list = bosses_sheet.range(f'B{starting_cell}:AX{len(names)+1}')
    skills_cell_list = skills_sheet.range(f'B{starting_cell}:AW{len(names)+1}')
    not_found = []


    for index,name in enumerate(names[starting_cell-2:], start=starting_cell):
        stats = getStats(playerURL(name,'iron'))
        if stats != "404":
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            player_bosses = [player_skills["Overall"]]+list(player_clues.values())+list(player_bosses.values())
            player_skills = list(player_skills.values())
            print(f"updating {name} total {player_skills[0]}")
            bosses_list.append(player_bosses)
            skills_list.append(player_skills)
        else:

            print(f"{name} not found in highscores.")
            bosses_list.append(bosses_values[index-2][1:])
            skills_list.append(skills_values[index-2][1:])
            not_found.append(name)

    bosses_list = [item for sublist in bosses_list for item in sublist]
    skills_list = [item for sublist in skills_list for item in sublist]


    for i, val in enumerate(bosses_list):  #gives us a tuple of an index and value
        if val:
            bosses_cell_list[i].value = int(val)

    for i, val in enumerate(skills_list):  #gives us a tuple of an index and value
        if val:
            skills_cell_list[i].value = int(val)

    bosses_sheet.update_cells(bosses_cell_list)
    skills_sheet.update_cells(skills_cell_list)


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
    if stat in STATSINDEX.keys():
        index = STATSINDEX[stat]
        boss = bosses_sheet.col_values(index)[1:]
        score1,score2 = int(boss[index1]),int(boss[index2])
        return   (1, score1,score2) if score1>score2 else (2,score1,score2)
    elif stat in SKILLS:
        index = SKILLS.index(stat)*2+2
        skill = skills_sheet.col_values(index)[1:]
        skill_xp = skills_sheet.col_values(index+1)[1:]
        xp1,xp2 = int(skill_xp[index1]),int(skill_xp[index2])
        lvl1,lvl2 = int(skill[index1]),int(skill[index2])
        return   (1, xp1,lvl1,xp2,lvl2) if xp1>xp2 else (2,xp1,lvl1,xp2,lvl2)
    else:
        return 404

if __name__ == "__main__":
    scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    bosses_sheet = client.open("07 Irons HiScore").get_worksheet(0)
    skills_sheet = client.open("07 Irons HiScore").get_worksheet(1)
    names = [x.lower() for x in bosses_sheet.col_values(1)[1:]]
    #update_player(bosses_sheet,skills_sheet,names,"no ge canvey")

    #not_found = update_all(bosses_sheet,skills_sheet,names)
    update_bosses_names(BOSSES,bosses_sheet)
    #print(compare_players(bosses_sheet,skills_sheet,names,"no ge canvey","ironrok","Magic"))
    #print(top_stat(bosses_sheet,skills_sheet,names,"Attack",7))
