import requests
import urllib.parse
from constants import *


def playerURL(rsn,gamemode):
  url = f'{BASE_URL}{GAMEMODE_URL[gamemode]}{STATS_URL}{urllib.parse.quote(rsn)}'
  return url




def getStats(URL):
  request = requests.get(url = URL)
  if request.status_code == 200:
    return request._content.decode("utf-8")
  else:
    return 404
def parseStats(stats_string):
  statsList = stats_string.split("\n")
  statsList = [x.split(",") for x in statsList][:-1]
  return statsList



def createDicts(statsList):
  skills = {}
  clues = {}
  bosses = {}
  for index,skill in enumerate(SKILLS):
    # skills[f"{skill}_Rank"] = statsList[index][0]
    skills[f"{skill}"] = statsList[index][1]
    skills[f"{skill}_Xp"] = statsList[index][2]

  for index,clue in enumerate(CLUES,start=index+4):
    # clues[f"{clue}_Rank"] = statsList[index][0]
    clues[f"{clue}"] = statsList[index][1]


  for index,boss in enumerate(BOSSES,start=index+2):
    # bosses[f"{boss}_Rank"] = statsList[index][0]
    bosses[f"{boss}"] = statsList[index][1]
  return (skills,clues,bosses)

if __name__ == '__main__':
  rsn = "CH Product"

  print(createDicts(parseStats(getStats(playerURL(rsn,'iron')))))
