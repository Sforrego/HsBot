
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
  'Total',
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
"derangedarch":"Deranged Archaeologist",
"mole":"Giant Mole",
"vetion":"Vetion",
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
"zammy":"Kril'Tsutsaroth",
"kriltrutsaroth":"Kril'Tsutsaroth",
"kril":"Kril'Tsutsaroth",
"zamorak":"Kril'Tsutsaroth",
"arma":"Kree'arra",
"armadyl":"Kree'arra",
"kreearra":"Kree'arra",
"kree":"Kree'arra",
"bandos":"General Graardor",
"graardor":"General Graardor",
"cox":"Chambers of Xeric",
"raids":"Chambers of Xeric",
"raidscm":"Chambers of Xeric: ChallengeMode",
"coxcm":"Chambers of Xeric: ChallengeMode",
"tob":"Theatre of Blood",
"raids2":"Theatre of Blood",
"beg":"Beginner",
"med":"Medium",
'abyssal_sire': 'Abyssal Sire',
'alchemical_hydra': 'Alchemical Hydra',
'barrows_chests': 'Barrows Chests',
'chambers_of_xeric': 'Chambers of Xeric',
'chambers_of_xeric:_challenge_mode': 'Chambers of Xeric: Challenge Mode',
'chaos_elemental': 'Chaos Elemental',
'chaos_fanatic': 'Chaos Fanatic',
'commander_zilyana': 'Commander Zilyana',
'corporeal_beast': 'Corporeal Beast',
'crazy_archaeologist': 'Crazy Archaeologist',
'dagannoth_prime': 'Dagannoth Prime',
'dagannoth_rex': 'Dagannoth Rex',
'dagannoth_supreme': 'Dagannoth Supreme',
'deranged_archaeologist': 'Deranged Archaeologist',
'general_graardor': 'General Graardor',
'giant_mole': 'Giant Mole',
'grotesque_guardians': 'Grotesque Guardians',
'kalphite_queen': 'Kalphite Queen',
'king_black_dragon': 'King Black Dragon',
"k'ril_tsutsaroth": "K'ril Tsutsaroth",
"gauntlet":"The Gauntlet",
'the_gauntlet': 'The Gauntlet',
'the_corrupted_gauntlet': 'The Corrupted Gauntlet',
'corrupted':'The Corrupted Gauntlet',
'theatre_of_blood': 'Theatre of Blood',
'thermonuclear_smoke_devil': 'Thermonuclear Smoke Devil',
'bryophyta': 'Bryophyta',
'hespori': 'Hespori',
'kraken': 'Kraken',
"kree'arra": "Kree'Arra",
'mimic': 'Mimic',
'obor': 'Obor',
'sarachnis': 'Sarachnis',
'scorpia': 'Scorpia',
'skotizo': 'Skotizo',
'tzkal-zuk': 'TzKal-Zuk',
'tztok-jad': 'TzTok-Jad',
'venenatis': 'Venenatis',
"vet'ion": "Vet'ion",
'vorkath': 'Vorkath',
'wintertodt': 'Wintertodt',
'zalcano': 'Zalcano',
'zulrah': 'Zulrah',
'zul':'Zulrah',
'cerberus':'Cerberus',
'callisto': 'Callisto'
}

STATSINDEX = {"Overall":2,
"Total":3,
"Beginner":4,
"Easy":5,
"Medium":6,
"Hard":7,
"Elite":8,
"Master":9,
"Abyssal Sire":10,
"Alchemical Hydra":11,
"Barrows Chests":12,
"Bryophyta":13,
"Callisto":14,
"Cerberus":15,
"Chambers of Xeric":16,
"Chambers of Xeric: Challenge Mode":17,
"Chaos Elemental":18,
"Chaos Fanatic":19,
"Commander Zilyana":20,
"Corporeal Beast":21,
"Crazy Archaeologist":22,
"Dagannoth Prime":23,
"Dagannoth Rex":24,
"Dagannoth Supreme":25,
"Deranged Archaeologist":26,
"General Graardor":27,
"Giant Mole":28,
"Grotesque Guardians":29,
"Hespori":30,
"Kalphite Queen":31,
"King Black Dragon":32,
"Kraken":33,
"Kree'Arra":34,
"K'ril Tsutsaroth":35,
"Mimic":36,
"Obor":37,
"Sarachnis":38,
"Scorpia":39,
"Skotizo":40,
"The Gauntlet":41,
"The Corrupted Gauntlet":42,
"Theatre of Blood":43,
"Thermonuclear Smoke Devil":44,
"TzKal-Zuk":45,
"TzTok-Jad":46,
"Venenatis":47,
"Vet'ion":48,
"Vorkath":49,
"Wintertodt":50,
"Zalcano":51,
"Zulrah":52}

NAMES_LOWER = {'total': 'Total', 'beginner': 'Beginner', 'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hard', 'elite': 'Elite', 'master': 'Master', 'overall': 'Overall', 'attack': 'Attack', 'defence': 'Defence', 'strength': 'Strength', 'hitpoints': 'Hitpoints', 'ranged': 'Ranged', 'prayer': 'Prayer', 'magic': 'Magic', 'cooking': 'Cooking', 'woodcutting': 'Woodcutting', 'fletching': 'Fletching', 'fishing': 'Fishing', 'firemaking': 'Firemaking', 'crafting': 'Crafting', 'smithing': 'Smithing', 'mining': 'Mining', 'herblore': 'Herblore', 'agility': 'Agility', 'thieving': 'Thieving', 'slayer': 'Slayer', 'farming': 'Farming', 'runecraft': 'Runecraft', 'hunter': 'Hunter', 'construction': 'Construction'
}

if __name__ == "__main__":
    newdict = {}
    for clue in CLUES:
        newdict[clue.lower()] = clue
    for skill in SKILLS:
        newdict[skill.lower()] = skill
    print(newdict)