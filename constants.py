
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


# BINGO

## TILES MATCHING BINGO SHEETS

TILES_TO_NUM={"raids":1,
"cox":1,
"dk":2,
"dks":2,
"wildy":3,
"demonic":4,
"nightmare":5,
"corp":5,
"mole":6,
"gwd":7,
"barrows":8,
"slayer":9,
"priff":10,
"wt":11,
"tempoross":11,
"zulrah":12,
"rc":13,
"agility":14,
"sceptre":15,
"pp":15,
"wc":16,
"mining":16,
"hunter":16,

}

# BINGO_HIDDEN=["Gnome Scarves for everyone! (6 out of 8 members must get a gnome scarf)",
# "Tears of Guthix! ( A random member of your team is rolled, they must gain 100k xp in their lowest skill. REMEMBER to post picture of your xp before and after the grind with the cc name at bingo-proof-team!)",
# "Upset the Balance! (A random member of your team is rolled, they must gain 500k xp in their highest [non 99] skill.  REMEMBER to post picture of your xp before and after the grind with the cc name at bingo-proof-team!)",
# "Spectator Sport! (Upon revealing this tile choose two other teams which must engage in a best of 3 runelink battle for a bonus challenge point)"]


# ADMIN

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

# HISCORES

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
  'Runecraft',
  'Hunter',
  'Construction',
]
CLUES = [
  'Clues total',
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
"Tempoross",
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
'clues':'Clues total',
"hydra":"Alchemical Hydra",
"rc": "Runecraft",
"runecrafting":"Runecraft",
"wc":"Woodcutting",
"hp":"Hitpoints",
"str":"Strength",
"def":"Defence",
"atk":"Attack",
"con":"Construction",
"total":"Overall",
"fm":"Firemaking"
}


NAMES_LOWER = {x.lower().replace(" ","_"):x for x in BOSSES+CLUES+SKILLS}

########## PSQL DB #############
stats_col_names = ['rsn', 'overall', 'overall_xp', 'attack', 'attack_xp', 'defence', 'defence_xp', 'strength', 'strength_xp', 'hitpoints', 'hitpoints_xp', 'ranged', 'ranged_xp', 'prayer', 'prayer_xp', 'magic', 'magic_xp', 'cooking', 'cooking_xp', 'woodcutting', 'woodcutting_xp', 'fletching', 'fletching_xp', 'fishing', 'fishing_xp', 'firemaking', 'firemaking_xp', 'crafting', 'crafting_xp', 'smithing', 'smithing_xp', 'mining', 'mining_xp', 'herblore', 'herblore_xp', 'agility', 'agility_xp', 'thieving', 'thieving_xp', 'slayer', 'slayer_xp', 'farming', 'farming_xp', 'runecraft', 'runecraft_xp', 'hunter', 'hunter_xp', 'construction', 'construction_xp', 'clues_total', 'beginner', 'easy', 'medium', 'hard', 'elite', 'master', 'abyssal_sire', 'alchemical_hydra', 'barrows_chests', 'bryophyta', 'callisto', 'cerberus', 'chambers_of_xeric', 'chambers_of_xeric:_challenge_mode', 'chaos_elemental', 'chaos_fanatic', 'commander_zilyana', 'corporeal_beast', 'crazy_archaeologist', 'dagannoth_prime', 'dagannoth_rex', 'dagannoth_supreme', 'deranged_archaeologist', 'general_graardor', 'giant_mole', 'grotesque_guardians', 'hespori', 'kalphite_queen', 'king_black_dragon', 'kraken', "kree'arra", "k'ril_tsutsaroth", 'mimic', 'nightmare', 'obor', 'sarachnis', 'scorpia', 'skotizo', 'tempoross','the_gauntlet', 'the_corrupted_gauntlet', 'theatre_of_blood', 'thermonuclear_smoke_devil', 'tzkal-zuk', 'tztok-jad', 'venenatis', "vet'ion", 'vorkath', 'wintertodt', 'zalcano', 'zulrah', 'created_at', 'updated_at']


if __name__ == "__main__":
    newdict = {}
    for clue in CLUES:
        newdict[clue.lower()] = clue
    for skill in SKILLS:
        newdict[skill.lower()] = skill
    print(newdict)
