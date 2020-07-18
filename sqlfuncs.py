import os
import psycopg2
from dotenv import load_dotenv
from time import time
from funcs import *

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

def sql_add_player_hs_historic(cur,name,stats):
    """
    Inserts a new row to the historic_stats table.
     """
    string_of_values = stats_to_string(stats)
    cur.execute(f"""INSERT INTO historic_stats VALUES ('{name}',{string_of_values},current_timestamp)""")


def sql_update_player_hs(cur,name,col_names,stats):
    """
    col_names is a lsit of all the column names of the table stats
    Updates the row corresponding to name with updated stats
    """

    player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
    list_of_values = list(player_skills.values())+list(player_clues.values())+list(player_bosses.values())

    string_of_values = ",".join(list_of_values)
    query = "UPDATE stats SET "
    for i,value in enumerate(list_of_values,start=1):
        stat_name = col_names[i] if "'" not in col_names[i] else col_names[i].replace("'", "''")
        query += f""" "{col_names[i]}" = {value},"""

    query = query[:-1]
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
            str_response += f"{i+1:<3} {tup[0]:<20} {str(tup[1])}\n"
        elif len(tup)==3:
            str_response += f"{i+1:<3} {tup[0]:<20} {str(tup[1])} {str(tup[2])}\n"

    return str_response

def is_skill(stat):
    """ checks if a stat is a skill return 1 if it is 0 if it isnt"""
    stat = coded_string(stat)
    stat_clean = get_stat(stat)

    if stat_clean in SKILLS:
        return 1
    elif stat_clean in BOSSES:
        return 0
    else:
        raise Exception(f"{stat} is not a  valid stat.")

def get_players_in_hs(cur):
    """ return a list of all the players in the stats table"""
    query = "SELECT rsn FROM stats";
    cur.execute(query)
    names = cur.fetchall()
    return [x[0] for x in names]

def get_player_stat(cur,name,stat,col_names):
    """ get a single player stat"""
    if stat not in col_names:
        raise Exception(f"{stat} is not a  valid stat.")
    query = f"""SELECT rsn,"{stat}" FROM stats WHERE rsn='{name}'"""
    cur.execute(query)
    response = cur.fetchall()
    return response

def change_player_name(cur,old_name,new_name,stats):
    query = f"""UPDATE stats SET rsn =  '{new_name}' WHERE rsn='{old_name}'"""
    cur.execute(query)

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

    # response = is_skill("Chambers of xeric")
    # response = top_stat_to_string(sql_top_stat(cur,"kree'arra",10,0,stats_col_names))
    response = get_player_stat(cur,"ironrok","kree'arra",stats_col_names)
    #
    #
    #
    #
    #
    print(response)
    conn.commit()
