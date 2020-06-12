
BASE_URL = 'http://services.runescape.com/m=hiscore_oldschool'
STATS_URL = 'index_lite.ws?player='
SCORES_URL = 'overall.ws?'
GAMEMODE_URL = {
  'dmm': '_deadman/',
  'dmmt': '_tournament/',
  'hc': '_hardcore_ironman/',
  'iron': '_ironman/',
  'main': '/',
  'sdmm': '_seasonal/',
  'ult': '_ultimate/',
}

BINGO_SKILLS=[
"Woodcutting",
"Fishing",
"Mining",
"Agility",
"Thieving",
"Slayer",
"Runecrafting",
"Firemaking",
"Hunter"
]

BINGO_TILES=["4 GWD Uniques",
"2 Wintertodt Uniques (No gloves/torch)",
"2 Cox or Tob purples",
"1 Champion Scroll",
"1 Pyramid Plunder Sceptre",
"Wildy Boss Ring or Dpick",
"4 DK rings",
"Medium Clue Boots",
"2 Zenytes",
"1 Master Unique",
"Blood Shard",
"10 Easy uniques",
"2 Slayer Boss uniques",
"16 Barrows Uniques",
"3 Wildy Demi Boss Shards",
"Hespori Bucket",
"1 Blessed D'hide piece from Hard Clues",
"Vorkath Head/Unique (NO guaranteed head)",
"Beginner Clue Slippers/Parrot",
"4 Zulrah Uniques",
"2 Fishing Trawler PIeces",
"Black mask or Jaw of basilisks"
]

BINGO_LIST=["1	Instantly finish a random tile",
"2	Re do a random finished tile",
"3	2x Item drop rate for a DICED tile (need to do 2x LESS)",
"4	0.5x Item drop rate for a DICED tile (need to do 2x MORE)",
"5	Nothing happens!",
"6	Double 1 tile and remove another by choice",
"7	Nothing happens!",
"8	Add 1 needed item to a random (DICED) tile of a CHOSEN team.",
"9	Remove 1 needed item from a random (DICED) tile of a CHOSEN team.",
"10	Nothing happens!"]
BINGO_BOSSES = [
    "Zulrah",
    "Grotesque Guardians",
    "Chaos Fanatic",
    "Scorpia",
    "Crazy Archaeologist",
    "Cerberus",
    "Callisto",
    "Venenatis",
    "Sarachnis",
    "Commander Zilyana",
    "K'ril Tsutsaroth",
    "Kree'Arra",
    "Giant Mole",
    "Hespori",
    "TzTok-Jad"

]

BINGO_TEAMS = ["1","2","3","4","5","6","7","8","ghost"]

Bingo_SKILL_TILES = {"Woodcutting":1000000,
    "Fishing":800000,
    "Mining":500000,
    "Agility":1000000,
    "Thieving":1500000,
    "Slayer":500000,
    "Runecrafting":400000,
    "Firemaking":2000000,
    "Hunter":1000000,
}

BINGO_BOSS_TILES = {
    "GWD":150,
    "Wildy":60,
    "Wildy_Demi":100,
    "Zulrah":128,
    "Grotesque Guardians":75,
    "Chaos Fanatic":100,
    "Scorpia":100,
    "Crazy Archaeologist":100,
    "Cerberus":128,
    "Callisto":30,
    "Venenatis":30,
    "Sarachnis":100,
    "Commander Zilyana":50,
    "K'ril Tsutsaroth":50,
    "Kree'Arra":50,
    "Giant Mole":75,
    "Hespori":10,
    "TzTok-Jad":3

}

RANKS = {
    'smiley':4,
    '1 banana':5,
    '2 banana':6,
    '3 banana':7,
    'bronze':8,
    'silver':9,
    'gold':10,
    "1nana":5,
    "2nana":6,
    "3nana":7,
    "1":5,
    "2":6,
    "3":7,
    "recruit":5,
    "corporal":6,
    "sergeant":7,
    "0":4
}

RANKS2 = {
    4:"Smiley",
    5:"Recruit",
    6:"Corporal",
    7:"Sergeant",
    8:"Lieutenant",
    9:"Captain",
    10:"General"

}

SKILLS = [
  'Overall',
  'Attack',
  'Defence',
  'Strength',
  'Hitpoints',
  'Ranged',
  'Prayer',
  'Magic',
  'Cooking',
  'Woodcutting',
  'Fletching',
  'Fishing',
  'Firemaking',
  'Crafting',
  'Smithing',
  'Mining',
  'Herblore',
  'Agility',
  'Thieving',
  'Slayer',
  'Farming',
  'Runecrafting',
  'Hunter',
  'Construction',
]
CLUES = [
  'Clues (total)',
  'Beginner',
  'Easy',
  'Medium',
  'Hard',
  'Elite',
  'Master',
]

BOSSES = [
'Abyssal Sire',
'Alchemical Hydra',
'Barrows Chests',
'Bryophyta',
'Callisto',
'Cerberus',
'Chambers of Xeric',
'Chambers of Xeric: Challenge Mode',
'Chaos Elemental',
'Chaos Fanatic',
'Commander Zilyana',
'Corporeal Beast',
'Crazy Archaeologist',
'Dagannoth Prime',
'Dagannoth Rex',
'Dagannoth Supreme',
'Deranged Archaeologist',
'General Graardor',
'Giant Mole',
'Grotesque Guardians',
'Hespori',
'Kalphite Queen',
'King Black Dragon',
'Kraken',
"Kree'Arra",
"K'ril Tsutsaroth",
"Mimic",
"Nightmare",
"Obor",
"Sarachnis",
"Scorpia",
"Skotizo",
"The Gauntlet",
"The Corrupted Gauntlet",
"Theatre of Blood",
"Thermonuclear Smoke Devil",
"TzKal-Zuk",
"TzTok-Jad",
"Venenatis",
"Vet'ion",
"Vorkath",
"Wintertodt",
"Zalcano",
"Zulrah"
]

boss_shorts = {
"corp":"Corporeal Beast",
"jad":"TzTok-Jad",
"kq":"Kalphite Queen",
"chaosele":"Chaos Elemental",
"crazyarch":"Crazy Archaeologist",
"crazy_arch":"Crazy Archaeologist",
"derangedarch":"Deranged Archaeologist",
"mole":"Giant Mole",
"vetion":"Vet'ion",
"vene":"Venenatis",
"kbd":"King Black Dragon",
"vork":"Vorkath",
"sire":"Abyssal Sire",
"cerb":"Cerberus",
"supreme":"Dagannoth Supreme",
"rex":"Dagannoth Rex",
"prime":"Dagannoth Prime",
"wt":"Wintertodt",
"barrows":"Barrows Chests",
"dusk":"Grotesque Guardians",
"dawn":"Grotesque Guardians",
"gargs":"Grotesque Guardians",
"smokedevil":"Thermonuclear Smoke Devil",
"thermy":"Thermonuclear Smoke Devil",
"inferno":"TzKal-Zuk",
"zuk":"TzKal-Zuk",
"sara":"Commander Zilyana",
"zily":"Commander Zilyana",
"zilyana":"Commander Zilyana",
"saradomin":"Commander Zilyana",
"zammy":"K'ril Tsutsaroth",
"kriltrutsaroth":"K'ril Tsutsaroth",
"kril":"K'ril Tsutsaroth",
"zamorak":"K'ril Tsutsaroth",
"arma":"Kree'Arra",
"armadyl":"Kree'Arra",
"kreearra":"Kree'Arra",
"kree":"Kree'Arra",
"bandos":"General Graardor",
"graardor":"General Graardor",
"cox":"Chambers of Xeric",
"raids":"Chambers of Xeric",
"raidscm":"Chambers of Xeric: Challenge Mode",
"coxcm":"Chambers of Xeric: Challenge Mode",
"tob":"Theatre of Blood",
"raids2":"Theatre of Blood",
"beg":"Beginner",
"med":"Medium",
'clues':'Clues (total)',
"hydra":"Alchemical Hydra",
"rc": "Runecrafting",
"wc":"Woodcutting",
"hp":"Hitpoints",
"str":"Strength",
"def":"Defence",
"atk":"Attack",
"con":"Construction"
}

# INDEX IN THE SPREADSHEET
STATSINDEX = {"Overall":2}
STATSINDEX.update({x:BOSSES.index(x)+10 for x in BOSSES})
STATSINDEX.update({x:CLUES.index(x)+3 for x in CLUES})

NAMES_LOWER = {x.lower().replace(" ","_"):x for x in BOSSES+CLUES+SKILLS}

if __name__ == "__main__":
    newdict = {}
    for clue in CLUES:
        newdict[clue.lower()] = clue
    for skill in SKILLS:
        newdict[skill.lower()] = skill
    print(newdict)
