import os
import psycopg2
from dotenv import load_dotenv
from time import time
from funcs import createDicts,parseStats,get_stat
from constants import SKILLS,BOSSES,CLUES,stats_col_names
from getstats import getStats, playerURL
def seconds_to_hours_mins(int):
    hours = int//3600
    mins = (int%3600)//60
    return hours,mins
def coded_string(string):
    return string.replace(" ", "_").lower()

def stats_to_string(stats):
    """ receives a string of  raw values turns them into a string ready to be inserted into the db"""
    player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
    list_of_values = list(player_skills.values())+list(player_clues.values())+list(player_bosses.values())
    string_of_values = ",".join(list_of_values)
    return string_of_values

def sql_add_player_hs(cur,name,stats):
    """
    cur is a cursor object from psql connection, name of a player, this player raw stats from osrs api
    Inserts a new row to the stats table.

     """
    string_of_values = stats_to_string(stats)
    cur.execute(f"""INSERT INTO stats VALUES ('{name}',{string_of_values},current_timestamp,current_timestamp)""")


def sql_update_player_hs(cur,name,stats,col_names):
    """
    col_names is a lsit of all the column names of the table stats
    Updates the row corresponding to name with updated stats
    """

    player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
    list_of_values = list(player_skills.values())+list(player_clues.values())+list(player_bosses.values())

    query = "UPDATE stats SET "
    for i,value in enumerate(list_of_values,start=1):
        query += f""" "{col_names[i]}" = {value},"""

    query += f""" updated_at = current_timestamp """
    query += f" WHERE rsn = '{name}'"

    cur.execute(query)

def sql_top_stat(cur,stat,n,skill,col_names):
    """
    n is the number of players we want to retrieve, skill is a boolean 1 if the stat is a skill 0 if not.
    retrieves the top n players in a certain stat
    """
    if stat not in col_names:
        raise Exception(f"{stat} is not a  valid stat.")
    if skill:
        query = f"""SELECT rsn,"{stat}","{stat}_xp" FROM stats ORDER BY ("{stat}","{stat}_xp") DESC LIMIT {n}"""
    else:
        query = f"""SELECT rsn,"{stat}" FROM stats ORDER BY "{stat}" DESC LIMIT {n}"""
    cur.execute(query)
    response = cur.fetchall()
    return response

def top_stat_to_string(response):
    """ Turns the response from sql_top_stat into a pretty string """
    str_response = ""
    for i,tup in enumerate(response):
        if len(tup)==2:
            str_response += f"{i+1:<3} {tup[0]:<14} {str(tup[1]):<5}\n"
        elif len(tup)==3:
            str_response += f"{i+1:<3} {tup[0]:<14} {str(tup[1]):<5} {str(tup[2]):<6}\n"

    return str_response

def is_skill(stat):
    """ checks if a stat is a skill return 1 if it is 0 if it isnt"""
    stat = coded_string(stat)
    stat_clean = get_stat(stat)

    if stat_clean in SKILLS:
        return 1
    elif stat_clean in BOSSES+CLUES:
        return 0
    else:
        raise Exception(f"{stat} is not a  valid stat.")

def get_players_in_hs(cur):
    """ return a list of all the players in the stats table"""
    query = "SELECT rsn FROM stats"
    cur.execute(query)
    names = cur.fetchall()
    return [x[0] for x in names]

def get_players_in_tracker(cur):
    """ return a list of all the players in the stats table"""
    query = "SELECT rsn FROM clan_tracker"
    cur.execute(query)
    names = cur.fetchall()
    return [x[0] for x in names]

def get_players_in_personal_tracker(cur):
    """ return a list of all the players in the personal_tracker table"""
    query = "SELECT rsn FROM personal_tracker"
    cur.execute(query)
    names = cur.fetchall()
    return [x[0] for x in names]

def get_player_stat(cur,name,stat,skill,col_names):
    """ get a single player stat"""
    if stat not in col_names:
        raise Exception(f"{stat} is not a  valid stat.")
    if skill:
        query = f"""SELECT rsn,"{stat}","{stat}_xp" FROM stats WHERE rsn='{name}'"""
    else:
        query = f"""SELECT rsn,"{stat}" FROM stats WHERE rsn='{name}'"""
    cur.execute(query)
    response = cur.fetchall()
    return response

def change_player_name(cur,old_name,new_name):
    query = f"""UPDATE stats SET rsn =  '{new_name}' WHERE rsn='{old_name}'"""
    cur.execute(query)

def change_player_name_mytracker(cur,old_name,new_name):
    query = f"""UPDATE personal_tracker SET rsn =  '{new_name}' WHERE rsn='{old_name}'"""
    cur.execute(query)
def change_player_name_clantracker(cur,old_name,new_name):
    query = f"""UPDATE clan_tracker SET rsn =  '{new_name}' WHERE rsn='{old_name}'"""
    cur.execute(query)

def get_player_rank(cur,name,stat,skill):
    if skill:
        query = f"""SELECT Row FROM (SELECT row_number() OVER(ORDER BY ("{stat}","{stat}_xp") DESC) AS Row,rsn FROM stats) as tempstats WHERE rsn='{name}' """
    else:
        query = f"""SELECT Row FROM (SELECT row_number() OVER(ORDER BY "{stat}" DESC) AS Row,rsn FROM stats) as tempstats WHERE rsn='{name}'"""
    cur.execute(query)
    response = cur.fetchall()
    return response[0][0]

def add_personal_tracker(cur,name,stats):
    string_of_values = stats_to_string(stats)
    cur.execute(f"""INSERT INTO personal_tracker VALUES ('{name}',{string_of_values},current_timestamp)""")

def add_clan_tracker(cur,name,stats):
    string_of_values = stats_to_string(stats)
    cur.execute(f"""INSERT INTO clan_tracker VALUES ('{name}',{string_of_values},current_timestamp)""")

def xp_gained_clan(cur,name,stat,skill):
    if skill:
        query = f"""SELECT s.{stat}_xp-t.{stat}_xp FROM stats as s, clan_tracker as t WHERE s.rsn = '{name}' and t.rsn = '{name}'  """
    else:
        query = f""" SELECT s."{stat}"-t."{stat}" FROM stats as s, clan_tracker as t WHERE s.rsn = '{name}' and t.rsn = '{name}' """
    cur.execute(query)
    stat_delta = cur.fetchone()[0]
    time_query = f"""SELECT s.updated_at-t.created_at FROM stats as s, clan_tracker as t WHERE s.rsn = '{name}' and t.rsn = '{name}'  """
    cur.execute(time_query)
    time_delta = cur.fetchone()[0]
    return (int(stat_delta),time_delta)

def xp_gained(cur,name,stat,skill):
    if skill:
        query = f"""SELECT s.{stat}_xp-t.{stat}_xp FROM stats as s, personal_tracker as t WHERE s.rsn = '{name}' and t.rsn = '{name}'  """
    else:
        query = f""" SELECT s."{stat}"-t."{stat}" FROM stats as s, personal_tracker as t WHERE s.rsn = '{name}' and t.rsn = '{name}' """
    cur.execute(query)
    stat_delta = cur.fetchone()[0]
    time_query = f"""SELECT s.updated_at-t.created_at FROM stats as s, personal_tracker as t WHERE s.rsn = '{name}' and t.rsn = '{name}'  """
    cur.execute(time_query)
    time_delta = cur.fetchone()[0]
    return (int(stat_delta),time_delta)

def reset_personal_tracker(cur,name):
    query = f"""Delete from personal_tracker where rsn = '{name}'  """
    cur.execute(query)

def tracker_starting_stat(cur,name,stat,skill,table):
    if skill:
        query = f"""SELECT "{stat}_xp" FROM {table} WHERE rsn = '{name}'  """
    else:
        query = f""" SELECT "{stat}" FROM {table} WHERE rsn = '{name}' """

    cur.execute(query)
    starting_stat = cur.fetchone()[0]
    return starting_stat

def tracker_starting_stat_multiple(cur,names,stat,skill,table):
    inside = "("
    for i,name in enumerate(names):
        if i == len(names)-1:
            inside += f"'{name}')"
        else:
            inside += f"'{name}',"
    if skill:
        query = f"""SELECT rsn,"{stat}_xp" FROM {table} WHERE rsn in {inside}  """
    else:
        query = f""" SELECT rsn,"{stat}" FROM {table} WHERE rsn in {inside} """

    cur.execute(query)
    print(query)
    starting_stat = cur.fetchall()
    return starting_stat

def top_tracked(cur,stat,skill,n):
    if skill:
        query = f"""SELECT s.rsn,s.{stat}_xp-t.{stat}_xp as xp_gained FROM stats as s, clan_tracker as t WHERE s.rsn = t.rsn  ORDER BY xp_gained DESC LIMIT {n}"""
    else:
        query = f""" SELECT s.rsn,s."{stat}"-t."{stat}" as kc_gained FROM stats as s, clan_tracker as t WHERE s.rsn = t.rsn and t."{stat}" != -1 ORDER BY kc_gained DESC LIMIT {n}"""
    cur.execute(query)
    return cur.fetchall()
def get_ranks(cur,name,skill):
    ranks = []
    if skill:
        for stat in SKILLS:
            rank = get_player_rank(cur,name,stat.lower(),skill)
            ranks.append((skill,rank))
    print(ranks)


def rm_from_hs(cur,name):
    query = f"""delete from stats where rsn='{name}'  """
    cur.execute(query)

def add_team(cur,team_num,players):
    query = f"""INSERT INTO teams VALUES ({team_num}"""
    for i,player in enumerate(players):
        player = player.lower()
        if i == len(players)-1:
            query += f""",'{player}')"""
        else:
            query += f""" ,'{player}' """
    print(query)
    cur.execute(query)

def update_team(cur,team_num,player_num,player):
    query = f"""UPDATE teams SET player{player_num} = '{player}' where team_number={team_num}"""
    cur.execute(query)

def get_team(cur,team_num):
    query = f"""select * from teams where team_number = {team_num} """
    cur.execute(query)
    team = cur.fetchall()
    return team[0][1:]

def get_team_nums(cur):
    query = f"""SELECT team_number from teams"""
    cur.execute(query)
    team_nums = cur.fetchall()
    team_nums = [x[0] for x in team_nums]
    return team_nums

def reset_teams(cur):
    query = """DELETE FROM teams """
    cur.execute(query)

def xp_gained_team(cur,stat,skill, players):
    inside = "("
    for i,player in enumerate(players):
        if i == len(players)-1:
            inside += f"'{player}')"
        else:
            inside += f"'{player}',"
    if skill:
        query = f"""SELECT sum(stats.{stat}_xp-clan_tracker.{stat}_xp) from stats inner join clan_tracker on (stats.rsn=clan_tracker.rsn) where stats.rsn IN {inside}"""
    else:
        query = f"""SELECT sum(stats."{stat}"-clan_tracker."{stat}") from stats inner join clan_tracker on (stats.rsn=clan_tracker.rsn) where stats.rsn IN {inside}"""
    print(query)
    cur.execute(query)
    stat_delta = cur.fetchone()[0]
    return int(stat_delta)

def bingo_gained(cur,stat,skill):
    players = []
    for i in range(1,7):
        players += get_team(cur,i)

    if not skill:
        starting_kc = tracker_starting_stat_multiple(cur,players,stat,skill,'clan_tracker')
        players = [x[0] for x in starting_kc if int(x[1]) != -1]


    inside = "("
    for i,player in enumerate(players):
        if i == len(players)-1:
            inside += f"'{player}')"
        else:
            inside += f"'{player}'',"
    query = f"""SELECT sum(stats."{stat}"-clan_tracker."{stat}") from stats inner join clan_tracker on (stats.rsn=clan_tracker.rsn) where stats.rsn IN {inside}"""
    cur.execute(query)
    stat_delta = cur.fetchone()[0]
    return int(stat_delta)

def get_all_from_hs(cur):
    query = """SELECT * from stats"""
    cur.execute(query)
    return cur.fetchall()

#def add_new_boss_hs(cur):
    # in the create table function add the new boss at the desired location.
    # then change stats,clantracker,personaltracker col names in constants and bosses to match the new boss.

    # alter table stats rename to oldstats
    # create table stats ("rsn" varchar(12), "overall" numeric, "overall_xp" numeric, "attack" numeric, "attack_xp" numeric, "defence" numeric, "defence_xp" numeric, "strength" numeric, "strength_xp" numeric, "hitpoints" numeric, "hitpoints_xp" numeric, "ranged" numeric, "ranged_xp" numeric, "prayer" numeric, "prayer_xp" numeric, "magic" numeric, "magic_xp" numeric, "cooking" numeric, "cooking_xp" numeric, "woodcutting" numeric, "woodcutting_xp" numeric, "fletching" numeric, "fletching_xp" numeric, "fishing" numeric, "fishing_xp" numeric, "firemaking" numeric, "firemaking_xp" numeric, "crafting" numeric, "crafting_xp" numeric, "smithing" numeric, "smithing_xp" numeric, "mining" numeric, "mining_xp" numeric, "herblore" numeric, "herblore_xp" numeric, "agility" numeric, "agility_xp" numeric, "thieving" numeric, "thieving_xp" numeric, "slayer" numeric, "slayer_xp" numeric, "farming" numeric, "farming_xp" numeric, "runecraft" numeric, "runecraft_xp" numeric, "hunter" numeric, "hunter_xp" numeric, "construction" numeric, "construction_xp" numeric, "clues_total" numeric, "beginner" numeric, "easy" numeric, "medium" numeric, "hard" numeric, "elite" numeric, "master" numeric, "abyssal_sire" numeric, "alchemical_hydra" numeric, "barrows_chests" numeric, "bryophyta" numeric, "callisto" numeric, "cerberus" numeric, "chambers_of_xeric" numeric, "chambers_of_xeric:_challenge_mode" numeric, "chaos_elemental" numeric, "chaos_fanatic" numeric, "commander_zilyana" numeric, "corporeal_beast" numeric, "crazy_archaeologist" numeric, "dagannoth_prime" numeric, "dagannoth_rex" numeric, "dagannoth_supreme" numeric, "deranged_archaeologist" numeric, "general_graardor" numeric, "giant_mole" numeric, "grotesque_guardians" numeric, "hespori" numeric, "kalphite_queen" numeric, "king_black_dragon" numeric, "kraken" numeric, "kree'arra" numeric, "k'ril_tsutsaroth" numeric, "mimic" numeric, "nightmare" numeric, "obor" numeric, "sarachnis" numeric, "scorpia" numeric, "skotizo" numeric, "tempoross" numeric, "the_gauntlet" numeric, "the_corrupted_gauntlet" numeric, "theatre_of_blood" numeric, "thermonuclear_smoke_devil" numeric, "tzkal-zuk" numeric, "tztok-jad" numeric, "venenatis" numeric, "vet'ion" numeric, "vorkath" numeric, "wintertodt" numeric, "zalcano" numeric, "zulrah" numeric, "created_at" TIMESTAMP, "updated_at" TIMESTAMP)
    # insert into stats ("rsn", "overall", "overall_xp", "attack", "attack_xp", "defence", "defence_xp", "strength", "strength_xp", "hitpoints", "hitpoints_xp", "ranged", "ranged_xp", "prayer", "prayer_xp", "magic", "magic_xp", "cooking", "cooking_xp", "woodcutting", "woodcutting_xp", "fletching", "fletching_xp", "fishing", "fishing_xp", "firemaking", "firemaking_xp", "crafting", "crafting_xp", "smithing", "smithing_xp", "mining", "mining_xp", "herblore", "herblore_xp", "agility", "agility_xp", "thieving", "thieving_xp", "slayer", "slayer_xp", "farming", "farming_xp", "runecraft", "runecraft_xp", "hunter", "hunter_xp", "construction", "construction_xp", "clues_total", "beginner", "easy", "medium", "hard", "elite", "master", "abyssal_sire", "alchemical_hydra", "barrows_chests", "bryophyta", "callisto", "cerberus", "chambers_of_xeric", "chambers_of_xeric:_challenge_mode", "chaos_elemental", "chaos_fanatic", "commander_zilyana", "corporeal_beast", "crazy_archaeologist", "dagannoth_prime", "dagannoth_rex", "dagannoth_supreme", "deranged_archaeologist", "general_graardor", "giant_mole", "grotesque_guardians", "hespori", "kalphite_queen", "king_black_dragon", "kraken", "kree'arra", "k'ril_tsutsaroth", "mimic", "nightmare", "obor", "sarachnis", "scorpia", "skotizo", "the_gauntlet", "the_corrupted_gauntlet", "theatre_of_blood", "thermonuclear_smoke_devil", "tzkal-zuk", "tztok-jad", "venenatis", "vet'ion", "vorkath", "wintertodt", "zalcano", "zulrah", "created_at", "updated_at") 
    # select 
    # "rsn", "overall", "overall_xp", "attack", "attack_xp", "defence", "defence_xp", "strength", "strength_xp", "hitpoints", "hitpoints_xp", "ranged", "ranged_xp", "prayer", "prayer_xp", "magic", "magic_xp", "cooking", "cooking_xp", "woodcutting", "woodcutting_xp", "fletching", "fletching_xp", "fishing", "fishing_xp", "firemaking", "firemaking_xp", "crafting", "crafting_xp", "smithing", "smithing_xp", "mining", "mining_xp", "herblore", "herblore_xp", "agility", "agility_xp", "thieving", "thieving_xp", "slayer", "slayer_xp", "farming", "farming_xp", "runecraft", "runecraft_xp", "hunter", "hunter_xp", "construction", "construction_xp", "clues_total", "beginner", "easy", "medium", "hard", "elite", "master", "abyssal_sire", "alchemical_hydra", "barrows_chests", "bryophyta", "callisto", "cerberus", "chambers_of_xeric", "chambers_of_xeric:_challenge_mode", "chaos_elemental", "chaos_fanatic", "commander_zilyana", "corporeal_beast", "crazy_archaeologist", "dagannoth_prime", "dagannoth_rex", "dagannoth_supreme", "deranged_archaeologist", "general_graardor", "giant_mole", "grotesque_guardians", "hespori", "kalphite_queen", "king_black_dragon", "kraken", "kree'arra", "k'ril_tsutsaroth", "mimic", "nightmare", "obor", "sarachnis", "scorpia", "skotizo", "the_gauntlet", "the_corrupted_gauntlet", "theatre_of_blood", "thermonuclear_smoke_devil", "tzkal-zuk", "tztok-jad", "venenatis", "vet'ion", "vorkath", "wintertodt", "zalcano", "zulrah", "created_at", "updated_at" from oldstats
    # alter table clan_tracker rename to oldclan_tracker
    # create table clan_tracker ("rsn" varchar(12), "overall" numeric, "overall_xp" numeric, "attack" numeric, "attack_xp" numeric, "defence" numeric, "defence_xp" numeric, "strength" numeric, "strength_xp" numeric, "hitpoints" numeric, "hitpoints_xp" numeric, "ranged" numeric, "ranged_xp" numeric, "prayer" numeric, "prayer_xp" numeric, "magic" numeric, "magic_xp" numeric, "cooking" numeric, "cooking_xp" numeric, "woodcutting" numeric, "woodcutting_xp" numeric, "fletching" numeric, "fletching_xp" numeric, "fishing" numeric, "fishing_xp" numeric, "firemaking" numeric, "firemaking_xp" numeric, "crafting" numeric, "crafting_xp" numeric, "smithing" numeric, "smithing_xp" numeric, "mining" numeric, "mining_xp" numeric, "herblore" numeric, "herblore_xp" numeric, "agility" numeric, "agility_xp" numeric, "thieving" numeric, "thieving_xp" numeric, "slayer" numeric, "slayer_xp" numeric, "farming" numeric, "farming_xp" numeric, "runecraft" numeric, "runecraft_xp" numeric, "hunter" numeric, "hunter_xp" numeric, "construction" numeric, "construction_xp" numeric, "clues_total" numeric, "beginner" numeric, "easy" numeric, "medium" numeric, "hard" numeric, "elite" numeric, "master" numeric, "abyssal_sire" numeric, "alchemical_hydra" numeric, "barrows_chests" numeric, "bryophyta" numeric, "callisto" numeric, "cerberus" numeric, "chambers_of_xeric" numeric, "chambers_of_xeric:_challenge_mode" numeric, "chaos_elemental" numeric, "chaos_fanatic" numeric, "commander_zilyana" numeric, "corporeal_beast" numeric, "crazy_archaeologist" numeric, "dagannoth_prime" numeric, "dagannoth_rex" numeric, "dagannoth_supreme" numeric, "deranged_archaeologist" numeric, "general_graardor" numeric, "giant_mole" numeric, "grotesque_guardians" numeric, "hespori" numeric, "kalphite_queen" numeric, "king_black_dragon" numeric, "kraken" numeric, "kree'arra" numeric, "k'ril_tsutsaroth" numeric, "mimic" numeric, "nightmare" numeric, "obor" numeric, "sarachnis" numeric, "scorpia" numeric, "skotizo" numeric, "tempoross" numeric, "the_gauntlet" numeric, "the_corrupted_gauntlet" numeric, "theatre_of_blood" numeric, "thermonuclear_smoke_devil" numeric, "tzkal-zuk" numeric, "tztok-jad" numeric, "venenatis" numeric, "vet'ion" numeric, "vorkath" numeric, "wintertodt" numeric, "zalcano" numeric, "zulrah" numeric, "created_at" TIMESTAMP, "updated_at" TIMESTAMP)
    # insert into clan_tracker ("rsn", "overall", "overall_xp", "attack", "attack_xp", "defence", "defence_xp", "strength", "strength_xp", "hitpoints", "hitpoints_xp", "ranged", "ranged_xp", "prayer", "prayer_xp", "magic", "magic_xp", "cooking", "cooking_xp", "woodcutting", "woodcutting_xp", "fletching", "fletching_xp", "fishing", "fishing_xp", "firemaking", "firemaking_xp", "crafting", "crafting_xp", "smithing", "smithing_xp", "mining", "mining_xp", "herblore", "herblore_xp", "agility", "agility_xp", "thieving", "thieving_xp", "slayer", "slayer_xp", "farming", "farming_xp", "runecraft", "runecraft_xp", "hunter", "hunter_xp", "construction", "construction_xp", "clues_total", "beginner", "easy", "medium", "hard", "elite", "master", "abyssal_sire", "alchemical_hydra", "barrows_chests", "bryophyta", "callisto", "cerberus", "chambers_of_xeric", "chambers_of_xeric:_challenge_mode", "chaos_elemental", "chaos_fanatic", "commander_zilyana", "corporeal_beast", "crazy_archaeologist", "dagannoth_prime", "dagannoth_rex", "dagannoth_supreme", "deranged_archaeologist", "general_graardor", "giant_mole", "grotesque_guardians", "hespori", "kalphite_queen", "king_black_dragon", "kraken", "kree'arra", "k'ril_tsutsaroth", "mimic", "nightmare", "obor", "sarachnis", "scorpia", "skotizo", "the_gauntlet", "the_corrupted_gauntlet", "theatre_of_blood", "thermonuclear_smoke_devil", "tzkal-zuk", "tztok-jad", "venenatis", "vet'ion", "vorkath", "wintertodt", "zalcano", "zulrah", "created_at", "updated_at") 
    # select 
    # "rsn", "overall", "overall_xp", "attack", "attack_xp", "defence", "defence_xp", "strength", "strength_xp", "hitpoints", "hitpoints_xp", "ranged", "ranged_xp", "prayer", "prayer_xp", "magic", "magic_xp", "cooking", "cooking_xp", "woodcutting", "woodcutting_xp", "fletching", "fletching_xp", "fishing", "fishing_xp", "firemaking", "firemaking_xp", "crafting", "crafting_xp", "smithing", "smithing_xp", "mining", "mining_xp", "herblore", "herblore_xp", "agility", "agility_xp", "thieving", "thieving_xp", "slayer", "slayer_xp", "farming", "farming_xp", "runecraft", "runecraft_xp", "hunter", "hunter_xp", "construction", "construction_xp", "clues_total", "beginner", "easy", "medium", "hard", "elite", "master", "abyssal_sire", "alchemical_hydra", "barrows_chests", "bryophyta", "callisto", "cerberus", "chambers_of_xeric", "chambers_of_xeric:_challenge_mode", "chaos_elemental", "chaos_fanatic", "commander_zilyana", "corporeal_beast", "crazy_archaeologist", "dagannoth_prime", "dagannoth_rex", "dagannoth_supreme", "deranged_archaeologist", "general_graardor", "giant_mole", "grotesque_guardians", "hespori", "kalphite_queen", "king_black_dragon", "kraken", "kree'arra", "k'ril_tsutsaroth", "mimic", "nightmare", "obor", "sarachnis", "scorpia", "skotizo", "the_gauntlet", "the_corrupted_gauntlet", "theatre_of_blood", "thermonuclear_smoke_devil", "tzkal-zuk", "tztok-jad", "venenatis", "vet'ion", "vorkath", "wintertodt", "zalcano", "zulrah", "created_at", "updated_at" from oldclan_tracker
    # alter table personal_tracker rename to oldpersonal_tracker
    # create table personal_tracker ("rsn" varchar(12), "overall" numeric, "overall_xp" numeric, "attack" numeric, "attack_xp" numeric, "defence" numeric, "defence_xp" numeric, "strength" numeric, "strength_xp" numeric, "hitpoints" numeric, "hitpoints_xp" numeric, "ranged" numeric, "ranged_xp" numeric, "prayer" numeric, "prayer_xp" numeric, "magic" numeric, "magic_xp" numeric, "cooking" numeric, "cooking_xp" numeric, "woodcutting" numeric, "woodcutting_xp" numeric, "fletching" numeric, "fletching_xp" numeric, "fishing" numeric, "fishing_xp" numeric, "firemaking" numeric, "firemaking_xp" numeric, "crafting" numeric, "crafting_xp" numeric, "smithing" numeric, "smithing_xp" numeric, "mining" numeric, "mining_xp" numeric, "herblore" numeric, "herblore_xp" numeric, "agility" numeric, "agility_xp" numeric, "thieving" numeric, "thieving_xp" numeric, "slayer" numeric, "slayer_xp" numeric, "farming" numeric, "farming_xp" numeric, "runecraft" numeric, "runecraft_xp" numeric, "hunter" numeric, "hunter_xp" numeric, "construction" numeric, "construction_xp" numeric, "clues_total" numeric, "beginner" numeric, "easy" numeric, "medium" numeric, "hard" numeric, "elite" numeric, "master" numeric, "abyssal_sire" numeric, "alchemical_hydra" numeric, "barrows_chests" numeric, "bryophyta" numeric, "callisto" numeric, "cerberus" numeric, "chambers_of_xeric" numeric, "chambers_of_xeric:_challenge_mode" numeric, "chaos_elemental" numeric, "chaos_fanatic" numeric, "commander_zilyana" numeric, "corporeal_beast" numeric, "crazy_archaeologist" numeric, "dagannoth_prime" numeric, "dagannoth_rex" numeric, "dagannoth_supreme" numeric, "deranged_archaeologist" numeric, "general_graardor" numeric, "giant_mole" numeric, "grotesque_guardians" numeric, "hespori" numeric, "kalphite_queen" numeric, "king_black_dragon" numeric, "kraken" numeric, "kree'arra" numeric, "k'ril_tsutsaroth" numeric, "mimic" numeric, "nightmare" numeric, "obor" numeric, "sarachnis" numeric, "scorpia" numeric, "skotizo" numeric, "tempoross" numeric, "the_gauntlet" numeric, "the_corrupted_gauntlet" numeric, "theatre_of_blood" numeric, "thermonuclear_smoke_devil" numeric, "tzkal-zuk" numeric, "tztok-jad" numeric, "venenatis" numeric, "vet'ion" numeric, "vorkath" numeric, "wintertodt" numeric, "zalcano" numeric, "zulrah" numeric, "created_at" TIMESTAMP, "updated_at" TIMESTAMP)
    # insert into personal_tracker ("rsn", "overall", "overall_xp", "attack", "attack_xp", "defence", "defence_xp", "strength", "strength_xp", "hitpoints", "hitpoints_xp", "ranged", "ranged_xp", "prayer", "prayer_xp", "magic", "magic_xp", "cooking", "cooking_xp", "woodcutting", "woodcutting_xp", "fletching", "fletching_xp", "fishing", "fishing_xp", "firemaking", "firemaking_xp", "crafting", "crafting_xp", "smithing", "smithing_xp", "mining", "mining_xp", "herblore", "herblore_xp", "agility", "agility_xp", "thieving", "thieving_xp", "slayer", "slayer_xp", "farming", "farming_xp", "runecraft", "runecraft_xp", "hunter", "hunter_xp", "construction", "construction_xp", "clues_total", "beginner", "easy", "medium", "hard", "elite", "master", "abyssal_sire", "alchemical_hydra", "barrows_chests", "bryophyta", "callisto", "cerberus", "chambers_of_xeric", "chambers_of_xeric:_challenge_mode", "chaos_elemental", "chaos_fanatic", "commander_zilyana", "corporeal_beast", "crazy_archaeologist", "dagannoth_prime", "dagannoth_rex", "dagannoth_supreme", "deranged_archaeologist", "general_graardor", "giant_mole", "grotesque_guardians", "hespori", "kalphite_queen", "king_black_dragon", "kraken", "kree'arra", "k'ril_tsutsaroth", "mimic", "nightmare", "obor", "sarachnis", "scorpia", "skotizo", "the_gauntlet", "the_corrupted_gauntlet", "theatre_of_blood", "thermonuclear_smoke_devil", "tzkal-zuk", "tztok-jad", "venenatis", "vet'ion", "vorkath", "wintertodt", "zalcano", "zulrah", "created_at", "updated_at") 
    # select 
    # "rsn", "overall", "overall_xp", "attack", "attack_xp", "defence", "defence_xp", "strength", "strength_xp", "hitpoints", "hitpoints_xp", "ranged", "ranged_xp", "prayer", "prayer_xp", "magic", "magic_xp", "cooking", "cooking_xp", "woodcutting", "woodcutting_xp", "fletching", "fletching_xp", "fishing", "fishing_xp", "firemaking", "firemaking_xp", "crafting", "crafting_xp", "smithing", "smithing_xp", "mining", "mining_xp", "herblore", "herblore_xp", "agility", "agility_xp", "thieving", "thieving_xp", "slayer", "slayer_xp", "farming", "farming_xp", "runecraft", "runecraft_xp", "hunter", "hunter_xp", "construction", "construction_xp", "clues_total", "beginner", "easy", "medium", "hard", "elite", "master", "abyssal_sire", "alchemical_hydra", "barrows_chests", "bryophyta", "callisto", "cerberus", "chambers_of_xeric", "chambers_of_xeric:_challenge_mode", "chaos_elemental", "chaos_fanatic", "commander_zilyana", "corporeal_beast", "crazy_archaeologist", "dagannoth_prime", "dagannoth_rex", "dagannoth_supreme", "deranged_archaeologist", "general_graardor", "giant_mole", "grotesque_guardians", "hespori", "kalphite_queen", "king_black_dragon", "kraken", "kree'arra", "k'ril_tsutsaroth", "mimic", "nightmare", "obor", "sarachnis", "scorpia", "skotizo", "the_gauntlet", "the_corrupted_gauntlet", "theatre_of_blood", "thermonuclear_smoke_devil", "tzkal-zuk", "tztok-jad", "venenatis", "vet'ion", "vorkath", "wintertodt", "zalcano", "zulrah", "created_at", "updated_at" from oldpersonal_tracker

if __name__ == '__main__':
    load_dotenv()

    user = os.getenv("user")
    password = os.getenv("password")
    host = os.getenv("host")
    port = os.getenv("port")
    database = os.getenv("database")

    conn = psycopg2.connect(user=user,password=password,host=host,port=port,database=database)
    cur = conn.cursor()



    ##### TESTING FUNCTIONS
    name = 'ironrok'
