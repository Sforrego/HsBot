This is a tracker bot for Oldschool Runescape, it connects Discord with SQL databases that are updated with data obtained from https://secure.runescape.com/m=hiscore_oldschool/a=13/overall. It's main purpose is to help tracking members stats within a community, this allows competitions to be automated and friendly competition between it's players, it's secondary purpose is to help organize a discord community, managing and tracking members and their roles.

It is no longer working since our friends at https://wiseoldman.net have done an excellent job in achieving the same goal as this bot, and any further work done here could be done helping them. The other reason is that everytime Jagex, the company running Oldschool Runescape, updates the game with a new boss or skill, all the stats move (because their API is pretty bad) and the bot stops being accurate, this implies continous updates to keep the bot working properly are needed.

### Commands

Replace spaces with _ in names.

Hiscores:

  add              Adds players to the clan's hiscores. !hs add <player1> <player2>
  
  change2          Changes the name in the clan's hiscores. !hs change2 <old_name> <new_name>
  
  check            Checks if a player is in the clan's hs. !hs check <name>
  
  fullupdate       Updates every player in the clan's hiscores. !hs fullupdate
  
  my               Gets the person using the command lvl/kc in a stat. !hs my <stat>
  
  rank             Shows the rank within the clan of a member in a specific stat. !hs rank <stat> <name>
  
  ranks            Shows the ranks within the clan of all the stats related to skills or bosses of a player. !hs ranks <"skills/bosses"> <name>
  rm               Removes names from the clan's hiscores. !hs rm <player1> <player2>
  rmoutdated       Removes outdated names from the clan's hiscores. !hs rmoutdated
  top              Shows the top 5 players and their kc/lvl+xp for a specific stat. !hs top <stat>
  top10            Shows the top 10 players and their kc/lvl+xp for a specific stat. !hs top10 <stat>
  update           Updates a players stats in the clan's hiscores. !hs update <player1> <player2>

Tracker:
  addtotracker     Adds players to the clan tracker. 
  checktracker     Checks a players progress according to the clan tracker. 
  mytracker        Check's xp/kills gained since being tracked with the perso...
  playerstracked   Checks which players are being tracked by the clan tracker. 
  resetclantracker Removes everyone from the clantracker
  resetmytracker   Resets a player's personal tracker'. 
  startmytracker   Starts a player's personal tracker. 
  toptracker       Checks the top 5 progress according to the clan tracker in...
  toptracker10     Checks the top 10 progress according to the clan tracker i...
  trackercommands  Shows all the tracker related commands
  updatetracker    Updates all players in the tracker.
  
Bingo:
  addteam          Add a team of players.
  bingocommands    Shows all the bingo related commands
  checkallteams    Checks xp/kc gained by all teams in a skill/boss (players ...
  checkdone        Checks tiles done by a team.
  checkleft        Checks tiles that have not been done by a team.
  checkteam        Checks xp/kc gained by a team in a skill/boss (players wit...
  complete         Completes a Tile.
  getteam          Returns the players of a specific team. !hs checkteam 1 ->...
  modifyteam       Updates a specific player of a team. !hs updateteam 1 5 ir...
  resetteams       Removes all teams.
  undo             Undo a Tile.
  updateteam       updates a bingo team on the hiscores. !hs updateteam 1
  
Management
  change           Changes a players rsn in the spreadsheets (Admin).
  clan_ranks       Return all players with a specific rank (Admin).
  due              Return all players due rank in the spreadsheets (Admin).
  help             Shows this message
  joindate         Shows a player and their join date.
  myjoindate       Shows your join date.
  remove           Removes players from the cc (sheets) (Admin) (Replace spac...
  shorts           Gets all the short ways of calling each stat (Case insensi...
  superadd         Changes a players discord nick, gives him role, and adds h...
